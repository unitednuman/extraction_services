import requests
from lxml import html
from scrappers.base_scrapper import *
from scrappers.traceback import save_error_report
from extraction_services.models import HouseAuction


payload = {}
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}


def parse_property(auction_url, auction_image, address, auction_price, is_sold, property_type, tenure, short_description):
    try:
        response = requests.request("GET", auction_url, headers=headers, data=payload, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='content1']")[0].text_content().strip()

        if not tenure:
            tenure = get_tenure(description)

        try:
            beds_div = get_text(result, 0, "//div[@class='stat-box__number']")
            no_of_beds = get_bedroom(beds_div)
        except Exception:
            no_of_beds = None
        if no_of_beds is None:
            no_of_beds = get_bedroom(short_description)
        if no_of_beds is None:
            no_of_beds = get_bedroom(description)
        auction_date = result.xpath("//h3[@class='auction-date']")[0].text_content()
        auction_date = parse_auction_date(auction_date)
        if guidePrice and address:
            data_hash = {
                "price": guidePrice,
                "currency_type": currency,
                "picture_link": auction_image,
                "property_description": description,
                "property_link": auction_url,
                "property_type": property_type,
                "tenure": tenure,
                "address": address,
                "postal_code": postal_code,
                "number_of_bedrooms": no_of_beds,
                "auction_datetime": auction_date,
                "source": "auctionestates.co.uk",
                # "is_sold":is_sold
            }
            HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)


def _run(url):
    response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        result = results.xpath("//li[@class='property-results__list--item']")

        for auction in result:
            try:

                is_sold = False
                if "Sold" in auction.text_content().strip():
                    continue
                auction_url = "https://www.auctionestates.co.uk" + auction.xpath(".//a")[0].attrib["href"]

                auction_image = auction.xpath(".//img")[0].attrib["src"].strip()
                if "http" not in auction_image:
                    auction_image = "https://www.auctionestates.co.uk" + auction_image

                short_description = (
                    auction.xpath(".//ul[@class='property-details__points-list']")[0].text_content().strip()
                )
                property_type = get_property_type(short_description)

                address = auction.xpath(".//div[@class='property-image__address']")[0].text_content().strip()
                address = " ".join(address.split())
                if property_type == "other" and "land" in address.lower():
                    property_type = "land"
                if "land" in address.lower():
                    address = re.search(r"(?<= to ).*|(?<= of ).*|(?<= at ).*", address, re.IGNORECASE)
                    if address:
                        address = address.group().strip()
                tenure = get_tenure(short_description)

                auction_price = auction.xpath(".//div[@class='property-details__price']")[0].text_content().strip()
                parse_property(
                    auction_url, auction_image, address, auction_price, is_sold, property_type, tenure, short_description
                )
            except:
                pass
        pagination = results.xpath(".//div[@class='pagination']/span")
        next_page_url = ""
        k = 0
        for pages in pagination:
            if "current" in pages.attrib["class"]:
                try:
                    next_page_url = (
                        "https://www.auctionestates.co.uk" + pagination[k + 1].xpath(".//a")[0].attrib["href"]
                    )
                    break
                except:
                    pass
            k += 1
        if next_page_url:
            _run(next_page_url)
    except BaseException as be:
        save_error_report(be, __file__)


def run():
    url = f"https://www.auctionestates.co.uk/view-properties"
    _run(url)
