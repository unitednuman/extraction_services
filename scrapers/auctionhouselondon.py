import requests

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

    def prepare_price(self, price):
        try:
            if 'sold' in price.lower():
                price = None
            else:
                price = float(price.split('-')[0].replace('£', '').replace('+', '').replace(',', ''))
        except Exception as ex:
            raise TypeError("Price convertion issue")
        return price

    def parser(self, data):
        data_array = []
        for json_data in data['result']['pageContext']['auctions']:
            for lot_details in json_data['Lots']:
                if not lot_details:
                    pass
                price = self.prepare_price(lot_details['GuidePrice'])
                if price == None:
                    pass
                full_address = lot_details['FullAddress']
                url_id = "-".join(full_address.replace(',','').split())
                lot_id = lot_details['ID']
                url = f"https://auctionhouselondon.co.uk/page-data/lot/{url_id}-{lot_id}/page-data.json".lower()
                try:
                    inner_res = self.connect_to(url)
                except Exception as ex:
                    raise Exception(f"URL issue {ex}")

                inner_details = inner_res.json()['result']['pageContext']
                auction_date = inner_details['AuctionDate']
                auction_hours = auction_date.split('T')[1]
                auc_hours = ":".join([auction_hours.split(":")[0], auction_hours.split(":")[1]])
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
                    "auctionDetails": {
                        "date": auction_date,
                        "hour": auc_hours,
                        "venue": None,
                    },
                    "domain": self.DOMAIN
                }
                data_array.append(data_hash)
        return data_array

    def scraper(self):
        response = self.connect_to(self.URL)
        data = response.json()
        item = []
        item = self.parser(data)


try:
    AuctionHouseLondon().scraper()
except Exception as e:
    print(e)
