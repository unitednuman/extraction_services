import requests
from lxml import html
from price_parser import Price
import re
import dateparser
from price_parser import Price
import logging
import json
from json import JSONDecodeError
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback, save_error_report
from extraction_services.models import HouseAuction, ErrorReport
import dateutil.parser as dparser


payload = {}
headers = {
    "authority": "www.dedmangray.co.uk",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
}


def parse_property(auction_url, auction_image, address, auction_price, no_of_beds, property_type, is_sold):
    try:
        response = requests.request("GET", auction_url, headers=headers, data=payload, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        auction_date = None
        guidePrice, currency = prepare_price(auction_price)
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@class='main styling']")[0].text_content()
        property_type1 = get_property_type(description)
        if property_type1:
            property_type = property_type1
        tenure = get_tenure(description)
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
            "source": "dedmangray.co.uk",
            # "is_sold":is_sold
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)


def _run(url, property_type):
    response = requests.request("GET", url, headers=headers, data=payload, timeout=10)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        result = results.xpath("//div[@data-wraplink='.link']")

        for auction in result:
            try:
                is_sold = False
                try:
                    if auction.xpath(".//div[@class='slash-sold']"):
                        continue
                except:
                    pass
                auction_url = "https://www.dedmangray.co.uk" + auction.xpath(".//a")[0].attrib["href"]
                auction_image = auction.xpath(".//img")[0].attrib["src"]
                if "http" not in auction_image:
                    auction_image = "https://www.dedmangray.co.uk" + auction_image
                address = ""
                try:
                    address = auction.xpath(".//strong[@style='font-size:14pt;']")[0].text_content()
                except:
                    pass
                auction_price = auction.xpath(".//p[@class='price']")[0].text_content().strip()
                bed_room_text = auction.xpath(".//div[@class='span55 push5 span-parent']/p")[1].text_content()
                no_of_beds = get_bedroom(bed_room_text)
                parse_property(auction_url, auction_image, address, auction_price, no_of_beds, property_type, is_sold)
            except:
                pass
        if next_page := results.xpath(".//a[contains(text(),'next »')]"):
            next_page_url = "https://www.dedmangray.co.uk" + next_page[0].attrib["href"]
            _run(next_page_url, property_type)
    except BaseException as be:
        save_error_report(be, __file__)


def run():
    property_types = ["commercial", "residential"]
    for property_type in property_types:
        url = f"https://www.dedmangray.co.uk/{property_type}-property/?formType=QuickSearch&sale_let=1&type=&location=all&min=&max=&min=&max=&submit=1&q=1"
        property_type = re.sub(r"%20|%2", " ", property_type)
        _run(url, property_type)
