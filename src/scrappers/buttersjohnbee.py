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

def parse_property(auction_url, auction_image , property_type, auction_price):
    try:
        response = requests.get(auction_url)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        auction_title = result.xpath("//h1[@class='section__title h2']")[0].text_content()
        guidePrice, currency = prepare_price(auction_price)
        address = result.xpath("//h1[@class='section__title h2']")[0].text_content().split(' in ')[1]
        description = result.xpath("//div[@class='col-md-8 section__content']")[0].text_content().strip()
        auction_date=re.search(r" on .*pm, | on .*am, | on .*am. | on .*pm. | at .* \nat | on .*pm ", description)
        auction_date=auction_date.group()
        auction_date=re.sub(r'(Monday)|(Tuesday)|(Wednesday)|(Thursday)|(Friday)|(Saturday)|(Sunday)|( at )|( \nat )| (on )',' ',auction_date).split(', ')[0].strip()
        auction_date=parse_auction_date(auction_date)
        if not property_type:
            property_type=get_property_type(description)
        postal_code = parse_postal_code(auction_title, __file__)
        tenure=get_tenure(description)
        try:
            response = requests.get(auction_url+"?layout=printdetails")
            result = html.fromstring(response.content)
            fix_br_tag_issue(result)
            no_of_beds =result.xpath(".//ul[@class='rooms']")[0].text_content()
            no_of_beds = get_bedroom(no_of_beds)
        except print(0):
            pass
        
        data_hash = {
            "price": guidePrice,
            "currency_type": currency,
            "picture_link": auction_image,
            "property_description": description,
            "property_link": auction_url,
            "property_type":property_type,
            "tenure":tenure,
            "address": address,
            "postal_code": postal_code,
            "number_of_bedrooms": no_of_beds,
            "auction_datetime": auction_date,
            "source": "buttersjohnbee.com"
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)

def run():
    # /page-2
    page=1
    while page<=5:
        pageno=""
        if page>1:
            pageno=f"/page-{page}"
        url = f"https://www.buttersjohnbee.com/auction-properties/properties-for-sale-in-staffordshire-and-cheshire{pageno}"
        response = requests.request("GET", url)
        results = html.fromstring(response.content)
        fix_br_tag_issue(results)
        try:
            i=0
            for auction in results.xpath("//div[@class='item infinite-item property for-sale-by-auction']"):
                auction_url = "https://www.buttersjohnbee.com"+auction.xpath(".//a")[0].attrib['href']
                auction_image = auction.xpath(".//div[@class='property__image']/img")[0].attrib['src']
                # property_type=auction.xpath("//div[@class='property__content']")[0].text_content()
                property_type = auction.xpath(".//div[@class='property__content']/text()[last()]")[0].strip()
                auction_price = auction.xpath(".//span[@class='price-qualifier']")[0].text_content().strip()
                parse_property(auction_url, auction_image , property_type, auction_price)
                i+=1
        except BaseException as be:
            save_error_report(be, __file__)
        if not results.xpath("//div[@class='item infinite-item property for-sale-by-auction']"):
            break
        page+=1    