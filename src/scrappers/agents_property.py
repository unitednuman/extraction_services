import requests
from lxml import html
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport


def parse_property(url, venue, auction_datetime):
    response = requests.get(url, timeout=10)
    result = html.fromstring(response.content)
    fix_br_tag_issue(result)
    address = result.xpath("//div[@class='single-property-galleries row u-bg-white col-wrapper flex-wrapper']//p")[
        0
    ].text
    postal_code = parse_postal_code(address, __file__)
    price, currency_symbol = prepare_price(result.xpath("//p[@class='single-property-price']")[0].text)
    imagelink = result.xpath("//div[@class='gallery-img']//img")[0].attrib["src"]
    property_title = result.xpath("//h1[@class='single-property-title']")[0].text
    property_type = get_property_type(property_title)
    description = result.xpath("//div[@class='tabs-container container']")[0].text_content()
    no_of_beds = None
    if "Bedroom" in property_title:
        no_of_beds = int(property_title.split("Bedroom")[0].strip())
    tenure, property_type, no_of_beds = get_beds_type_tenure(tenure, property_type, no_of_beds, description)

    data_hash = {
        "price": price,
        "currency_type": currency_symbol,
        "picture_link": imagelink,
        "property_description": description,
        "property_link": response.url,
        "address": address,
        "postal_code": postal_code,
        "number_of_bedrooms": no_of_beds,
        "auction_datetime": auction_datetime,
        "auction_venue": venue,
        "tenure": tenure,
        "property_type": property_type,
        "source": "agentspropertyauction.com",
    }
    HouseAuction.sv_upd_result(data_hash)


def run():
    url = "https://www.agentspropertyauction.com/next-auction/"
    response = requests.request("GET", url, timeout=10)
    result = html.fromstring(response.content)
    fix_br_tag_issue(result)
    venue = result.xpath("//h1[@class='hero-subtitle']")[0].text
    auction_datetime = (
        result.xpath("//p[@class='hero-title']")[0].text
        + " "
        + result.xpath("//p[@class='hero-subtitle']")[0].text.split("-")[0]
    )
    auction_datetime = parse_auction_date(auction_datetime)
    for property in result.xpath("//a[@class='u-link-cover']"):
        try:
            property_url = property.xpath(".")[0].attrib["href"]
            parse_property(property_url, venue, auction_datetime)
        except BaseException as be:
            save_error_report(be, __file__)
            # _traceback = get_traceback()
            # if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
            #     error_report.count = error_report.count + 1
            #     error_report.save()
            # else:
            #     ErrorReport.objects.create(file_name="agents_property.py", error=str(be), trace_back=_traceback)
