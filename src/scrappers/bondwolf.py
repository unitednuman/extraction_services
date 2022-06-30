import time
from lxml import html
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport
from playwright.sync_api import sync_playwright

start_url = "https://www.bondwolfe.com/auctions/properties/?location=&minprice=&maxprice=&type="


def parse_property(page, url):
    page.goto(url)
    time.sleep(5)
    response = page.content()
    result = html.fromstring(response)
    auction_time = parse_auction_date(
        result.xpath("//div[@class='AuctionDetails-datetime']//h2")[0].text_content().strip())
    description = result.xpath("//h4[contains(text(), 'Property Description')]//parent::div")[0].text_content().strip()

    tenure_str = get_text(result, 0, "//h4[contains(text(), 'Tenure')]//parent::div")
    tenure = get_tenure(tenure_str)
    price_text = result.xpath("//h2[@class='h1 mb-1 PropertyHeader-price-value']")[0].text_content().strip()
    price, currency = prepare_price(price_text)
    address = result.xpath("//div[@class='PropertyHeader-description pr-lg-5']//h1")[0].text_content().strip()
    postal_code = parse_postal_code(address)
    imagelink = result.xpath("//div[@class='slick-list draggable']//img")[0].attrib['src']
    propertyLink = page.url
    venue = get_text(result, 0, "//div[@class='AuctionDetails-location']//p")
    data_hash = {
        # "_id": details["version"]["allsop_auctionid"],
        "price": price,
        "currency_type": currency,
        "picture_link": imagelink,
        "property_description": description,
        "property_link": propertyLink,
        "address": address,
        "postal_code": postal_code,
        "auction_datetime": auction_time,
        "auction_venue": venue,
        "source": "bondwolfe.com"
    }
    if house_auction := HouseAuction.objects.filter(property_link=url):
        house_auction.update(**data_hash)
    else:
        HouseAuction.objects.create(**data_hash)


def start():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url)
        page.locator("//label[@for='postPerPage5']").first.click()
        result = html.fromstring(page.content())
        if result.xpath("//h3[contains(text(), 'Properties coming soon.')]"):
            print("No Properties Found")
            browser.close()
            return

        for property in result.xpath("//a[@class='PropertyCard']"):
            try:
                url = property.xpath('.')[0].attrib['href']
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
