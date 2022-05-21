import requests

from extraction_services.models import HouseAuction


class AllSop:
    DOMAIN = 'https://auctions.allsop.co.uk'
    URL = 'https://auctions.allsop.co.uk/api/search?future_auctions=on&page=1&size=500&sortOrder=Max%20Price'

    def __init__(self):
        pass

    def connect_to(self, url, payload={}):  # fixme {}
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
        # fixme : none type object error
        price = price.split('-')[0].replace('£', '').replace('+', '').replace(",", "")
        if 'M' in price:
            return float(price.replace("M", '')) * 1000000
        else:
            return float(price) * 100000  # fixme : why multply with fix value

    def parser(self, data):

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
                "auction_datetime": auction_date, #TODO : combine date and hour
                # "auction_hour": auc_hours,  combine it with auction_date_time
                "auction_venue": details['version']['allsop_auction']['allsop_venue'],
                "source": "auctionhouse.co.uk"
            }

            if house_auction := HouseAuction.objects.filter(property_link=res.url):
                house_auction.update(**data_hash)
            else:
                HouseAuction.objects.create(**data_hash)

    def scraper(self):
        response = self.connect_to(self.URL)
        item = []
        items = self.parser(response.json())
        # insertion needs to be done yet


def run():
    AllSop().scraper()


