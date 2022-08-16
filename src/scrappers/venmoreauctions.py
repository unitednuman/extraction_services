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
  'authority': 'www.venmoreauctions.co.uk',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-language': 'en-US,en;q=0.9',
  'cache-control': 'max-age=0',
  'referer': 'https://www.venmoreauctions.co.uk/',
  'sec-ch-ua': '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
}





def parse_property(auction_url, auction_image,address , auction_price,is_sold):
    try:
        response = requests.request("GET", auction_url, headers=headers, data=payload)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='section-description']")[0].text_content()
        property_type=get_property_type(description)
        if 'tenant-in-situ' in description:
            tenure='Leasehold'
        else:
            tenure="Freehold"
        no_of_beds = get_bedroom(description)
        auction_date= result.xpath("//span[@class='font-light f-greatprimer c-red mini-1']")[0].text_content().strip().split('-')[1]
        auction_date=parse_auction_date(auction_date)
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
            "source": "venmoreauctions.co.uk",
            "is_sold":is_sold,
            "auction_venue":"Online Auction"
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)

def _run(url):        
    response = requests.request("GET", url, headers=headers, data=payload)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        result=results.xpath("//div[@class='property-strip-block']")
        
        for auction in result:
            try:
                is_sold=False
                if 'SOLD PRIOR' in auction.text_content():
                    is_sold=True
                auction_url = 'https://www.venmoreauctions.co.uk/'+auction.xpath(".//a")[0].attrib['href']
                auction_image = auction.xpath(".//img")[0].attrib['src']
                if 'http' not in auction_image:
                    auction_image='https://www.venmoreauctions.co.uk/'+auction_image
                
                address = auction.xpath(".//span[@class='f-body-copy db marbot10']")[0].text_content()
                
                
                if is_sold:
                    auction_price="£0"
                else:
                    auction_price = auction.xpath(".//span[@class='font-bold f-greatprimer tar db p-text-green']")[0].text_content().strip()
                
                parse_property(auction_url, auction_image,address , auction_price,is_sold)
            except:
                pass
        try:    
            if next_page:=results.xpath(".//a[contains(text(),'Next ')]")[0].attrib['href']:
                next_page_url='https://www.venmoreauctions.co.uk'+next_page
                _run(next_page_url)
        except:pass
    except BaseException as be:
        save_error_report(be, __file__)  
        
def run():
    url = f"https://www.venmoreauctions.co.uk/Property-Search"
    _run(url)
        
        
        
  

