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

property_map_local={
    "Flat Apartment":"semi detached",
    "Hotel Guesthouse":"Commercial", 
    "Commercial Property":"Commercial", 
    "Public Convenience":"Commercial"
}

# "Block%20of%20Apartments","Bungalow","Caravan%2FPark%20Home","Commercial%20Property",
# "Detached","Farm%20House%2FBarn%20Conversion","Flat%2FApartment","Hotel%2FGuesthouse",
# "Land","Other","Parking%2FGarages","Public%20Convenience","Retirement%20Property","Semi%20Detached",
# "Terraced"

def parse_property(auction_url, auction_image , auction_title, auction_price,property_type):
    try:
        response = requests.get(auction_url, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        auction_date=None
        try:
            auction_date= result.xpath("//span[@class='inline-block vertical-middle line-height-1pt4 font-size-18 font-size-24-print font-weight-600 colour-blue margin-b5']")[1].text_content().replace('- Bidding opens','').strip()
            auction_date=parse_auction_date(auction_date)
        except:
            try:
                auction_date= result.xpath("//span[@class='inline-block vertical-middle line-height-1pt4 font-size-18 font-size-24-print font-weight-600 colour-blue margin-b5']")[0].text_content().replace('- Bidding opens','').strip()
                auction_date=parse_auction_date(auction_date)
            except:
                pass
        guidePrice, currency = prepare_price(auction_price)
        address = result.xpath("//address")[0].text_content()
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='property-details']")[0].text_content()
        floors =get_text(result, 0, "//div[@id='property-details']//table")
        
        tenure=get_tenure(description)
        
        if floors:
            no_of_beds =get_bedroom(floors)
        else:
            no_of_beds =get_bedroom(description)
        
        
        property_type_temp=get_property_type(description)
        if property_type_temp=="other":
            property_type_temp=get_property_type(property_type)
        if property_type_temp!="other":
            property_type=property_type_temp
        elif property_type in property_map_local:
            property_type = property_map_local[property_type]
        else:
            property_type="other"
        
        
        
        
        if property_type=="Land":
            no_of_beds=None
        
        if auction_date:
            data_hash = {
                "price": guidePrice,
                "currency_type": currency,
                "picture_link": auction_image,
                "property_description": description,
                "property_link": auction_url,
                "property_type":property_type.lower(),
                "tenure":tenure,
                "address": address,
                "postal_code": postal_code,
                "number_of_bedrooms": no_of_beds,
                "auction_datetime": auction_date,
                "source": "pugh-auctions.com",
                "auction_venue":"Online Auction"
            }
            HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)

def _run(url,property_type):        
    response = requests.request("GET", url, timeout=10)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        result=results.xpath("//div[@class='property-listing padding-20 ']") + results.xpath("//div[@class='property-listing padding-20 even']")
        
        for auction in result:
            try:
                auction_url = auction.xpath(".//a")[0].attrib['href']
                auction_image = auction.xpath(".//img[@class='width-100']")[0].attrib['src']
                auction_title = auction.xpath(".//a")[1].text_content()
                auction_price = auction.xpath(".//div[@class='block font-size-26 font-weight-600']")[0].text_content().strip()
                parse_property(auction_url, auction_image , auction_title, auction_price,property_type)
            except:
                pass    
        if next_page:=results.xpath("//li[@title='Go to Next Page']")[0]:
            next_page_url=next_page.xpath(".//a")[0].attrib['href']
            # if '&page=' in url:
            #     urls=url.split('&page=')
            #     next_page_url=urls[0]+"&page="+str(int(urls[1])+1)
            _run(next_page_url,property_type)
    except BaseException as be:
        save_error_report(be, __file__)  
        
def run():
    property_types=["Block%20of%20Apartments","Bungalow","Caravan%2FPark%20Home","Commercial%20Property","Detached","Farm%20House%2FBarn%20Conversion","Flat%2FApartment","Hotel%2FGuesthouse","Land","Other","Parking%2FGarages","Public%20Convenience","Retirement%20Property","Semi%20Detached","Terraced"]
    for property_type in property_types:
        url = f"https://www.pugh-auctions.com/property-search?filter-postcode-town=&filter-property-type={property_type}&filter-guide_price_from=&filter-guide_price_to=&filter-radius=5&filter-date_added=anytime&filters=1"
        property_type=re.sub(r"%2F|%20"," ",property_type)
        _run(url,property_type)
        
        
        
  

