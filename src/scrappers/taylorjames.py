import requests
from lxml import html
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction, ErrorReport


def parse_property(property_url, auction_datetime, auction_venue, imagelink):
    response = requests.get(property_url)
    result = html.fromstring(response.content)
    fix_br_tag_issue(result)
    no_of_beds = get_text(result, 0, "//span[@class='property-detail-icon property-detail-icon-beds']/span")
    guide_price = prepare_price(result.xpath("//div[@class='price']")[0].text_content())[0]
    currency_symbol = prepare_price(result.xpath("//div[@class='price']")[0].text_content())[1]
    address = result.xpath("//div[@class='col col-xs-12 col-sm-12 col-md-7 col-lg-7 col-xl-7']/h1")[0].text_content()
    postal_code = parse_postal_code(address, __file__)
    description = result.xpath("//div[@data-tab-content='tab_key_features']")[0].text_content()
    data_hash = {
        "price": guide_price,
        "currency_type": currency_symbol,
        "picture_link": imagelink,
        "property_description": description,
        "property_link": property_url,
        "address": address,
        "postal_code": postal_code,
        "number_of_bedrooms": no_of_beds,
        "auction_datetime": auction_datetime,
        "auction_venue": auction_venue,
        "source": "taylorjamesauctions.co.uk"
    }
    HouseAuction.sv_upd_result(data_hash)


def parse_auction(auction_url, auction_venue):
    response = requests.get(auction_url)
    result = html.fromstring(response.content)
    fix_br_tag_issue(result)
    auction_datetime = parse_auction_date(
        result.xpath("//h1//parent::div")[0].text_content().replace("Auction", "").replace("Bidding opens at",
                                                                                           "").strip())
    for property in result.xpath("//a[@class='property-link plus-hover']"):
        try:
            property_url = property.xpath(".")[0].attrib["href"]
            imagelink = property.xpath(".//img[contains(@alt,'property')]")[0].attrib['src']
            parse_property(property_url, auction_datetime, auction_venue, imagelink)
        except BaseException as be:
            save_error_report(be, __file__)


def run():
    url = "https://www.taylorjamesauctions.co.uk/property-auctions/"
    response = requests.request("GET", url)
    result = html.fromstring(response.content)
    fix_br_tag_issue(result)
    count = 0
    for auction in result.xpath("//div[@class='container auction']//div[@class='row']"):
        if count >= 2:
            break
        auction_venue = auction.xpath(".//p[contains(text(), 'Venue')]")[0].text_content()
        auction_url = auction.xpath(".//div[@class='past-only']/a")[0].attrib['href']
        parse_auction(auction_url, auction_venue)
        count += 1
