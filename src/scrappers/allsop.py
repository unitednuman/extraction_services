import requests
import os
import json
import re
import datetime
from extraction_services.models import HouseAuction , ErrorReport


class AllSop:
    DOMAIN = 'https://auctions.allsop.co.uk'
    URL = 'https://auctions.allsop.co.uk/api/search?future_auctions=on&page=1&size=500&sortOrder=Max%20Price'

    def __init__(self):
        pass

    def connect_to(self, url, payload={}):
        headers = {
            'authority': 'auctions.allsop.co.uk',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
            'x-powered-by': 'React 15.7.0',
        }

        re = requests.get(url, headers=headers, data=payload)
        return re

    def prepare_price(self, price):
        price = price.split('-')[0].replace('£', '').replace('+', '')
        if 'M' in price:
            return float(price.replace("M", '')) * 1000000
        else:
            return float(price) * 100000

    def parser(self, data):
        data_array = []
        for json_data in data['data']['results']:
            reference_no = "-".join(json_data["reference"].split())
            url = f"https://auctions.allsop.co.uk/api/lot/reference/{reference_no}?react"
            res = self.connect_to(url)
            details = res.json()
            price_str = details['version']['lot']['guide_price_text']
            price = self.prepare_price(price_str)
            auction_date = details['version']['allsop_auction']['allsop_auctiondate']
            auction_hours = auction_date.split('T')[1]
            auc_hours = ":".join([auction_hours.split(":")[0], auction_hours.split(":")[1]])
            features = "\n".join([value['value'] for value in details["version"]['features']])
            image_id = details["version"]['images'][0]['file_id']
            image_url = f"https://ams-auctions-production-storage.s3.eu-west-2.amazonaws.com/image_cache/{image_id}---auto--.jpg"
            data_hash = {
                # "_id": details["version"]["allsop_auctionid"],
                "price": price,
                "picture_link": image_url,
                "property_description": features,
                "property_link": res.url,
                "address": details["version"]['allsop_property']['allsop_name'],
                "postal_code": details["version"]['allsop_property']['allsop_postcode'],
                "number_of_bedrooms": details["version"]['allsop_property']['allsop_bedrooms'],
                "property_type": details['version']['tenancy_type'],
                "tenure": details['version']['allsop_propertytenure'],
                "auction_date": auction_date,
                "auction_hour": auc_hours,
                "auction_venue": details['version']['allsop_auction']['allsop_venue'],
                "domain": "https://www.auctionhouse.co.uk/"
            }

            try:
                HouseAuction.objects.create(**data_hash)
            except BaseException as be:
                print(be)
                ErrorReport.objects.create(file_name="model error", error=str(be))

            data_array.append(data_hash)

        return data_array

    def scraper(self):
        response = self.connect_to(self.URL)
        item = []
        items = self.parser(response.json())
        # insertion needs to be done yet


def run():
    AllSop().scraper()
