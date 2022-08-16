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

def parse_property(auction_url, auction_image , auction_title, auction_price,postal_code):
    try:
        response = requests.get(auction_url)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        address = auction_title
        
        description = result.xpath("//div[@class='fullDescription footerGap']")[0].text_content()
        property_type=get_property_type(description)
        tenure=get_tenure(description)
        no_of_beds = get_bedroom(description)
        auction_date=None
        try:
            auction_date= result.xpath("//span[contains(text(),'Auction: ')]")[0].text_content().replace('Auction: ','').strip()
            auction_date=parse_auction_date(auction_date)
        except:
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
            "source": "suttonkersh.co.uk"
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)




def run():
    url = "https://www.suttonkersh.co.uk/properties/listview/?auctionLocation=&availableOnly=on&FormSearchTextField=&geolat=&geolon=&georad=&section=auction&searchAuction=Search&auctionPeriod=128&lotNumber=&auctionType=all"
    response = requests.request("GET", url)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        i=0
        result=results.xpath("//table/tbody/tr")
        for auction in result:
            if 'detail_' in auction.attrib['id']:
                i+=1
                continue
            auction_title = auction.xpath(".//td")[1].text_content()
            auction_price = auction.xpath(".//td")[3].text_content().strip()
            postal_code= auction.xpath(".//td")[2].text_content()
            mauction=result[i+1]
            auction_url = 'https://www.suttonkersh.co.uk'+mauction.xpath(".//a")[0].attrib['href']
            auction_image = 'https://www.suttonkersh.co.uk'+mauction.xpath(".//img[@class='lotImage']")[0].attrib['src']
            parse_property(auction_url, auction_image , auction_title, auction_price,postal_code)
            i+=1
    except BaseException as be:
        save_error_report(be, __file__)    
