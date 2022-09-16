import requests
from django.utils.text import slugify
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback, save_error_report
from extraction_services.models import HouseAuction, ErrorReport
import dateparser
import re
from price_parser import parse_price


class AllSop:
    DOMAIN = 'https://auctions.allsop.co.uk'
    URL = 'https://auctions.allsop.co.uk/api/search?future_auctions=on&page=1&size=5000&sortOrder=Max%20Price'

    def __init__(self):
        pass

    def connect_to(self, url):  # fixme {}
        headers = {
            'authority': 'auctions.allsop.co.uk',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
            'x-powered-by': 'React 15.7.0',
        }

        res = requests.get(url, headers=headers, timeout=10)
        return res

    def currency_iso_name(self, currency_symbol):
        symbols = {
            "£": "GBP",
            "$": "USD",
        }
        try:
            return symbols[currency_symbol]
        except:
            raise Exception(f"Currency symbol \"{currency_symbol}\" not matching with available ones.")

    def parser(self, data):

        for json_data in data['data']['results']:
            try:
                reference_no = "-".join(json_data["reference"].split())
                url = f"https://auctions.allsop.co.uk/api/lot/reference/{reference_no}?react"
                res = self.connect_to(url)
                details = res.json()
                if 'M' in details['version']['lot']['guide_price_text']:
                    price_obj = parse_price(details['version']['lot']['guide_price_text'])
                    price = price_obj.amount_float * 1000000
                else:
                    price_obj = parse_price(details['version']['lot']['guide_price_text'])
                    price = price_obj.amount_float
                currency = self.currency_iso_name(price_obj.currency)
                auction_date = dateparser.parse(details['version']['allsop_auction']['allsop_auctiondate'])
                features = "\n".join([value['value'] for value in details["version"]['features']])
                image_id = details["version"]['images'][0]['file_id']
                image_url = f"https://ams-auctions-production-storage.s3.eu-west-2.amazonaws.com/image_cache/{image_id}---auto--.jpg"
                url_suffix = details["version"]['allsop_propertybyline']
                # char_to_replace = {'!': '','@': '','#': '','$':'','%':'','&':'','*':'','"':''}
                # url_suffix = re.sub(r"[!@#$%&*]",lambda x: char_to_replace[x.group(0)],url_suffix)
                # url_suffix = "-".join(url_suffix.strip().split()).strip().lower()
                slug = slugify(url_suffix)
                property_url = f"https://auctions.allsop.co.uk/lot-overview/{slug}/{reference_no}"
                property_type = get_property_type(details['version']['tenancy_type'])
                if property_type == "other":
                    property_type = get_property_type(features)
                data_hash = {
                    # "_id": details["version"]["allsop_auctionid"],
                    "price": price,
                    "currency_type": currency,
                    "picture_link": image_url,
                    "property_description": features,
                    "property_link": property_url,
                    "address": details["version"]['allsop_property']['allsop_name'],
                    "postal_code": details["version"]['allsop_property']['allsop_postcode'],
                    "number_of_bedrooms": details["version"]['allsop_property']['allsop_bedrooms'],
                    "property_type": property_type,
                    "tenure": details['version']['allsop_propertytenure'],
                    "auction_datetime": auction_date,
                    "auction_venue": details['version']['allsop_auction']['allsop_venue'],
                    "source": "auctions.allsop.co.uk"
                }
                HouseAuction.sv_upd_result(data_hash)
            except BaseException as be:
                save_error_report(be, __file__)

    def scraper(self):
        response = self.connect_to(self.URL)
        self.parser(response.json())


def run():
    AllSop().scraper()
