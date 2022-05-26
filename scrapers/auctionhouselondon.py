import requests
import dateparser
from price_parser import parse_price

class AuctionHouseLondon:
    DOMAIN = 'https://auctionhouselondon.co.uk/'
    URL = 'https://auctionhouselondon.co.uk/page-data/future-auctions/page-data.json'

    def __init__(self):
        pass

    def connect_to(self, url, headers={}, payload={}):
        print(url)
        re = requests.get(url, headers=headers, data=payload)
        print(f"------ Request Response : {re.status_code} --------")
        return re

    def parser(self, data):
        data_array = []
        for json_data in data['result']['pageContext']['auctions']:
            for lot_details in json_data['Lots']:
                if not lot_details:
                    pass
                price = parse_price(lot_details['GuidePrice']).amount_float if lot_details['GuidePrice'] else None
                full_address = lot_details['FullAddress']
                url_id = "-".join(full_address.replace(',','').split())
                lot_id = lot_details['ID']
                url = f"https://auctionhouselondon.co.uk/page-data/lot/{url_id}-{lot_id}/page-data.json".lower()
                inner_res = self.connect_to(url)
                inner_details = inner_res.json()['result']['pageContext']
                auction_date = dateparser.parse(inner_details['AuctionDate']).timestamp() * 1000 if inner_details['AuctionDate'] else None
                data_hash = {
                    "_id": lot_id,
                    "guidePrice": price,
                    "pictureLink": lot_details['Thumbnail'],
                    "propertyDescription": inner_details['Description'],
                    "propertyLink": url.replace('page-data.json','').replace('/page-data',''),
                    "address": full_address,
                    "postcode": lot_details['PostCode'],
                    "numberOfBedrooms": inner_details['Bedrooms'],
                    "propertyType": inner_details['PropertyType'],
                    "tenure": inner_details['TenureType'],
                    "auction_datetime": auction_date,
                    "auction_venue": None,
                    "domain": self.DOMAIN
                }
                data_array.append(data_hash)
        return data_array

    def scraper(self):
        response = self.connect_to(self.URL)
        data = response.json()
        item = []
        item = self.parser(data)



def run():
    AuctionHouseLondon().scraper()
