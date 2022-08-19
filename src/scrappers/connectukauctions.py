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


payload={}
headers = {
  'authority': 'realtime.connectukauctions.co.uk',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'max-age=0',
  'referer': 'https://connectukauctions.co.uk/',
  'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-site',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}





def parse_property(auction_url, auction_image,address , auction_price,is_sold,auction_date):
    try:
        response = requests.request("GET", auction_url, headers=headers, data=payload)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='tab-description']")[0].text_content().strip()
        property_type=get_property_type(description)
        tenure=get_tenure(description)
        no_of_beds = get_bedroom(description)
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
            "source": "connectukauctions.co.uk",
            # "is_sold":is_sold
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)




def _run(url):        
    response = requests.request("GET", url, headers=headers, data=payload)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        result=results.xpath("//li[contains(@class,'ast-col-sm-12 ast-article-post astra-woo-hover-swap uwa_auction_status_pending product type-product')]")
        
        for auction in result:
            try:
                
                is_sold=False
                
                auction_url = auction.xpath(".//a")[0].attrib['href']
                
                auction_image = auction.xpath(".//img")[0].attrib['src'].strip()
                
                try:
                    address = auction.xpath(".//h2[@class='woocommerce-loop-product__title']")[0].text_content().strip().split(' – ')[1]
                except:
                    address = auction.xpath(".//h2[@class='woocommerce-loop-product__title']")[0].text_content().strip()
                
                auction_date=auction.xpath(".//span[@class='ast-woo-product-category']")[0].text_content().strip()
                auction_date=parse_auction_date(auction_date)
                
                auction_price = auction.xpath(".//span[@class='guideprice']")[0].text_content().strip()
                parse_property(auction_url, auction_image,address , auction_price,is_sold,auction_date)
            except:
                pass  
        
    except BaseException as be:
        save_error_report(be, __file__)  
        
def run():
    url = f"https://realtime.connectukauctions.co.uk/"
    _run(url)
        
        
        
  

