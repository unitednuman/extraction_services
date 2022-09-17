import re

from lxml import html
import requests

from scrappers.base_scrapper import parse_postal_code, get_tenure, fix_br_tag_issue, get_property_type
from scrappers.traceback import save_error_report
import dateparser
from extraction_services.models import HouseAuction
from price_parser import Price

base_url = "https://www.sdlauctions.co.uk"


def get_text(node, index, xpath, raise_error=True):
    try:
        return node.xpath(xpath)[index].text_content()
    except Exception as e:
        if not raise_error:
            print("attribute finding error", e, xpath)
            return ""
        return ValueError(f"Unable to get text for {xpath}", e)


def get_attrib(node, xpath, index, attribute):
    try:
        return node.xpath(xpath)[index].attrib[attribute]
    except Exception as e:
        print("attribute finding error", e, attribute)
        return ""


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
        auction_date = auction_date.strip().split("\t")[-1].strip()
        auction_date = dateparser.parse(auction_date)
        return auction_date
    except Exception as e:
        raise ValueError("Unable to parse auction date", e)


def parse_properties(results):
    for property in results.xpath("//div[@class='auction-card']//div[@class='auction-card--content']"):

        propertyLink = base_url + get_attrib(property, "a", 0, "href")
        property_type = get_property_type(propertyLink)
        numberOfBedrooms = get_text(property, 0, ".//i[@class='fa fa-bed']//following-sibling::span", False)
        address = get_text(property, 0, ".//li[@class='auction-card--contend-address']")
        postcode = parse_postal_code(address, __file__)
        price = get_text(property, 0, ".//li[@class='auction-card--guide-price']//following-sibling::li")
        guidePrice = prepare_price(price)[0]
        currency = prepare_price(price)[1]
        auction_date = get_text(property, 0, "//b[contains(text(), 'Auction date:')]//parent::li")
        auction_date = parse_auction_date(auction_date)
        response = requests.get(propertyLink, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        propertyDescription = get_text(
            result, 0, "//div[contains(text(),'Property Description:')]//following-sibling::p"
        )
        tenure_str = get_text(result, 0, "//div[contains(text(),'Tenure: ')]//following-sibling::p")
        tenure = get_tenure(tenure_str)
        pictureLink = get_attrib(result, "//a[@data-lightbox='property-image']//img", 1, "src")
        data_hash = {
            # "_id": details["version"]["allsop_auctionid"],
            "price": guidePrice,
            "currency_type": currency,
            "picture_link": pictureLink,
            "property_description": propertyDescription,
            "property_link": propertyLink,
            "address": address,
            "postal_code": postcode,
            "number_of_bedrooms": numberOfBedrooms,
            "auction_datetime": auction_date,
            "tenure": tenure,
            "property_type": property_type,
            "source": "sdlauctions.co.uk",
        }
        # print(data_hash)
        HouseAuction.sv_upd_result(data_hash)


def parse_auctions(results):
    for auction in results.xpath("//div[@class='events-list']//div[@class='btn-flex-holder']"):
        try:
            auction_id = int(auction.xpath("a")[0].attrib["href"].split("/")[2])
            url = "https://www.sdlauctions.co.uk/wp-content/themes/sdl-auctions/library/property-functions.php"
            payload = {
                "func": "ajaxProp",
                "data": f"location=&minBeds=&maxBeds=&minPrice=&maxPrice=&lat=&lng=&bounds=&tempType=auction&search=1&radius=3&auctionId={auction_id}&include%5B%5D=&limit=All&page=1&order=Lot Number&oos=0",
            }
            response = requests.post(url, data=payload, timeout=10)
            results = html.fromstring(response.content)
            fix_br_tag_issue(results)
            parse_properties(results)
        except BaseException as be:
            save_error_report(be, __file__)


def run():
    response = requests.get("https://www.sdlauctions.co.uk/property-auctions/auction-events/", timeout=10)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    parse_auctions(results)
