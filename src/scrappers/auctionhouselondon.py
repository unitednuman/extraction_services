import requests
import dateparser
from price_parser import parse_price
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport


class AuctionHouseLondon:
    DOMAIN = 'https://auctionhouselondon.co.uk/'
    URL = 'https://auctionhouselondon.co.uk/page-data/future-auctions/page-data.json'

    def __init__(self):
        pass

    def connect_to(self, url, headers={}, payload={}):
        # print(url)
        res = requests.get(url, headers=headers, data=payload)
        # print(f"------ Request Response : {res.status_code} --------")
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
        for json_data in data['result']['pageContext']['auctions']:
            for lot_details in json_data['Lots']:
                try:
                    if not lot_details:
                        pass
                    parsed_price = parse_price(lot_details['GuidePrice']) if lot_details['GuidePrice'] else None
                    price = parsed_price.amount_float
                    currency = self.currency_iso_name(parsed_price.currency)
                    full_address = lot_details['FullAddress']
                    url_id = "-".join(full_address.replace(',', '').split())
                    lot_id = lot_details['ID']
                    url = f"https://auctionhouselondon.co.uk/page-data/lot/{url_id}-{lot_id}/page-data.json".lower()
                    inner_res = self.connect_to(url)
                    inner_details = inner_res.json()['result']['pageContext']
                    auction_date = dateparser.parse(inner_details['AuctionDate'])
                    data_hash = {
                        #"_id": lot_id,
                        "price": price,
                        "currency_type": currency,
                        "picture_link": lot_details['Thumbnail'],
                        "property_description": inner_details['Description'],
                        "property_link": url.replace('page-data.json', '').replace('/page-data', ''),
                        "address": full_address,
                        "postal_code": lot_details['PostCode'],
                        "number_of_bedrooms": inner_details['Bedrooms'],
                        "property_type": inner_details['PropertyType'],
                        "tenure": inner_details['TenureType'],
                        "auction_datetime": auction_date,
                        "auction_venue": None,
                        "source": "auctionhouselondon.co.uk"
                    }
                    if house_auction := HouseAuction.objects.filter(property_link=res.url):
                        house_auction.update(**data_hash)
                    else:
                        HouseAuction.objects.create(**data_hash)
                except BaseException as be:
                    _traceback = get_traceback()
                    if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                        error_report.count = error_report.count + 1
                        error_report.save()
                    else:
                        ErrorReport.objects.create(file_name="auctionhouselondon.py", error=str(be),
                                                   trace_back=_traceback)

    def scraper(self):
        response = self.connect_to(self.URL)
        data = response.json()
        self.parser(data)


def run():
    AuctionHouseLondon().scraper()
