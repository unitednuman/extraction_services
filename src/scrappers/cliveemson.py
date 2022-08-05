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

def get_bedroom(text):
    numRooms = re.search(r'(\w+\+?) *(?:double +)?-?bed(?:room)?s?|bed(?:room)?s?:? *(\d+\+?)', text, re.IGNORECASE)
    if (numRooms):
        if (numRooms.group(1) is not None):
            return numRooms.group(1)
        elif (numRooms.group(2) is not None):
            return numRooms.group(2)
    return None

def convert_words_to_integer(word):
    numbers = { "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10 }
    try:
        return numbers[word.strip()]
    except:
        raise Exception(f"word numbers \"{word}\" not matching with available ones.")
    
    return None


def parse_property(auction_url, auction_image , auction_title, auction_price,auction_date):
    try:
        response = requests.get(auction_url)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        guidePrice, currency = prepare_price(auction_price)
        address = result.xpath("//address[@class='lot-address']")[0].text_content()
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//section[@class='single-content single-lot-content']")[0].text_content()
        property_type_text=result.xpath("//section[@class='single-content single-lot-content']/p")[0].text_content()
        property_type=get_property_type(property_type_text)
        tenure_text=result.xpath("//section[@class='single-content single-lot-content']/h4[last()]")[0].text_content()
        tenure=get_tenure(tenure_text)
        no_of_beds =get_bedroom(auction_title)
        if no_of_beds is None:
            no_of_beds =get_bedroom(description)
        if no_of_beds is not None:
            no_of_beds=convert_words_to_integer(no_of_beds.lower())
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
            "source": "cliveemson.co.uk"
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)

def helpers():
    payload='search%5Blocation%5D=&search%5Bcoords%5D=&search%5Bdistance%5D=10000000&search%5Bvenue%5D=&search%5Blot%5D='
    headers = {
    'authority': 'www.cliveemson.co.uk',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    # 'cookie': 'PHPSESSID=r2k2bvo0rgk7cqna7qr5mmm5a0; CEA_CookieConsent={%22essential%22:true%2C%22functional%22:true%2C%22analytic%22:true}; CEA_ListingsView=grid',
    'origin': 'https://www.cliveemson.co.uk',
    'referer': 'https://www.cliveemson.co.uk/search/',
    'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    
    return payload,headers

payload, headers = helpers()



def run():
    url = "https://www.cliveemson.co.uk/properties/"
    response = requests.request("POST", url, headers=headers, data=payload)
    results = html.fromstring(response.content)
    fix_br_tag_issue(results)
    try:
        for result in results.xpath("//div[@class='auction auction-listings']"):
            auction_date = get_text(result, 0, "//div[@class='auction-info']")
            # .split(': ')[1].replace(' Auction','').strip()
            auction_date=re.sub('["\r\t\n]',"",auction_date)
            auction_date=dparser.parse(auction_date, fuzzy=True)
            for auction in result.xpath("//div[@class='tile-col lot-status--available']"):
                auction_url = auction.xpath(".//a[@class='tile-block-link']")[0].attrib['href']
                auction_image = auction.xpath(".//div[@class='tile-image lot-image']/span")[0].attrib['data-image-url']
                auction_title = auction.xpath(".//h3[@class='tile-heading lot-name']/a")[0].text_content()
                auction_price = auction.xpath(".//div[@class='lot-status']/strong")[0].text_content().strip()
                parse_property(auction_url, auction_image , auction_title, auction_price,auction_date)
    except BaseException as be:
        save_error_report(be, __file__)    

