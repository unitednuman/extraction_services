import time

import requests
from lxml import html
import dateparser
from price_parser import Price
import json
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport
from playwright.sync_api import sync_playwright

start_url = "https://www.bondwolfe.com/wp-admin/admin-ajax.php"

payload = "action=get_properties&page=1&total_pages=1&postsperpage=-1&orderby=lotnumber&location=&radius=&type=&minprice=&maxprice=&auction=&get_map=false&security=be579822a5"
headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://www.bondwolfe.com',
    'referer': 'https://www.bondwolfe.com/auctions/properties/?location=&minprice=&maxprice=&type=&status=undefined&show=-1&pages=1&radius=&orderby=lotnumber&auction_id=',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest'
}


def get_text(node, index, xpath):
    try:
        return node.xpath(xpath)[index].text_content().strip()
    except Exception as e:
        print("attribute finding error", e, xpath)
        return ''


def currency_iso_name(currency):
    symbols = {
        "£": "GBP",
        "$": "USD",
    }
    try:
        return symbols[currency]
    except:
        return "Currency Not Found"


def prepare_price(price):
    price_str = Price.fromstring(price)
    price = price_str.amount_float
    currency = price_str.currency
    currency = currency_iso_name(currency)
    return price, currency


def parse_auction_date(auction_date):
    try:
        auction_date = dateparser.parse(auction_date)
        return auction_date
    except Exception as e:
        raise ValueError("Unable to parse auction date", e)


def parse_property(page, url):
    page.goto(url)
    time.sleep(5)
    response = page.content()
    result = html.fromstring(response)
    status = result.xpath("//div[@class='PropertyHeader-price-result']")[0].text_content().strip()
    auction_time = parse_auction_date(
        result.xpath("//div[@class='AuctionDetails-datetime']//h2")[0].text_content().strip())
    description = result.xpath("//h4[contains(text(), 'Property Description')]//parent::div")[0].text_content().strip()

    tenure = get_text(result, "//h4[contains(text(), 'Tenure')]//parent::div", 0)

    price_text = result.xpath("//h2[@class='h1 mb-1 PropertyHeader-price-value']")[0].text_content().strip()
    price = prepare_price(price_text)[0]
    currency = prepare_price(price_text)[1]
    address = result.xpath("//div[@class='PropertyHeader-description pr-lg-5']//h1")[0].text_content().strip()
    postal_code = address.split(',')[-1]
    domain = "https://www.bondwolfe.com/"
    imagelink = result.xpath("//div[@class='slick-list draggable']//img")[0].attrib['src']
    propertyLink = page.url
    venue = get_text(result, "//div[@class='AuctionDetails-location']//p", 0)
    data_hash = {
        # "_id": details["version"]["allsop_auctionid"],
        "price": price,
        "currency_type": "$",  # TODO: Add currency type
        "picture_link": imagelink,
        "property_description": description,
        "property_link": url,
        "address": address,
        "postal_code": postal_code,
        "auction_datetime": auction_time,  # TODO : combine date and hour
        # "auction_hour": auc_hours,  combine it with auction_date_time
        "auction_venue": venue,
        "source": "https://www.bondwolfe.com/"
    }
    if house_auction := HouseAuction.objects.filter(property_link=url):
        house_auction.update(**data_hash)
    else:
        HouseAuction.objects.create(**data_hash)


def start():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        response = requests.request("POST", start_url, headers=headers, data=payload)
        json_data = json.loads(response.content)
        result = html.fromstring(json_data['data']['html'])

        for property in result.xpath("//a[@class='PropertyCard']"):
            try:
                url = property.xpath('.')[0].attrib['href']
                # print(url)
                parse_property(page, url)
            except BaseException as be:
                _traceback = get_traceback()
                if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                    error_report.count = error_report.count + 1
                    error_report.save()
                else:
                    ErrorReport.objects.create(file_name="bondwolf.py", error=str(be), trace_back=_traceback)


def run():
    start()
