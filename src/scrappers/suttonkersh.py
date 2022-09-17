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
from datetime import datetime


def parse_property(auction_url, auction_image, auction_title, auction_price, postal_code):
    try:
        response = requests.get(auction_url, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        address = auction_title

        description = result.xpath("//div[@class='fullDescription footerGap']")[0].text_content().strip()

        tenure = get_tenure(description)
        no_of_beds = get_bedroom(description)
        introduction = result.xpath("//div[@id='introduction']")[0].text_content()
        if no_of_beds is None:
            no_of_beds = get_bedroom(introduction)
        property_type = get_property_type(introduction)

        if "other" == property_type:
            property_type = get_property_type(auction_title)

        if "other" == property_type:
            property_type = get_property_type(description)

        auction_date = None
        try:
            auction_date = (
                result.xpath("//span[contains(text(),'Auction: ')]")[0].text_content().replace("Auction: ", "").strip()
            )
            day, month, year = tuple(map(int, auction_date.split("/")))
            auction_date = datetime(year, month, day)
        except:
            pass
        if auction_date:
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
                "source": "suttonkersh.co.uk",
                "auction_venue": "Online Auction",
            }
            HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)


def run():
    url = "https://www.suttonkersh.co.uk/properties/listview/?auctionLocation=&availableOnly=on&FormSearchTextField=&geolat=&geolon=&georad=&section=auction&searchAuction=Search&auctionPeriod=128&lotNumber=&auctionType=all"
    response = requests.request("GET", url, timeout=10)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        i = 0
        result = results.xpath("//table/tbody/tr")
        for auction in result:
            if "detail_" in auction.attrib["id"]:
                i += 1
                continue
            auction_title = auction.xpath(".//td")[1].text_content()
            auction_price = auction.xpath(".//td")[3].text_content().strip()
            postal_code = auction.xpath(".//td")[2].text_content()
            mauction = result[i + 1]
            auction_url = (
                "https://www.suttonkersh.co.uk" + mauction.xpath(".//a")[0].attrib["href"].split("/?s=listview")[0]
            )
            auction_image = (
                "https://www.suttonkersh.co.uk" + mauction.xpath(".//img[@class='lotImage']")[0].attrib["src"]
            )
            parse_property(auction_url, auction_image, auction_title, auction_price, postal_code)
            i += 1
    except BaseException as be:
        save_error_report(be, __file__)
