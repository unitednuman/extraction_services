import requests
from scrappers.traceback import get_traceback
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction, ErrorReport


class AuctionHouseLondon:
    DOMAIN = "https://auctionhouselondon.co.uk/"
    URL = "https://auctionhouselondon.co.uk/page-data/future-auctions/page-data.json"

    def __init__(self):
        pass

    def connect_to(self, url, headers=None, payload=None):
        # print(url)
        res = requests.get(url, headers=headers, data=payload, timeout=10)
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
            raise Exception(f'Currency symbol "{currency_symbol}" not matching with available ones.')

    def parser(self, data):
        for json_data in data["result"]["pageContext"]["auctions"]:
            for lot_details in json_data["Lots"]:
                try:
                    if not lot_details:
                        pass
                    if not "Sold Prior" in lot_details["GuidePrice"]:
                        price, currency = prepare_price(lot_details["GuidePrice"])
                    else:
                        price = 0.0
                        currency = ""
                    full_address = lot_details["FullAddress"]
                    url_id = "-".join(full_address.replace(",", "").split())
                    lot_id = lot_details["ID"]
                    url = f"https://auctionhouselondon.co.uk/page-data/lot/{url_id}-{lot_id}/page-data.json".lower()
                    inner_res = self.connect_to(url)
                    try:
                        inner_details = inner_res.json()["result"]["pageContext"]
                    except:
                        continue
                    auction_date = dateparser.parse(inner_details["AuctionDate"])
                    data_hash = {
                        # "_id": lot_id,
                        "price": price,
                        "currency_type": currency,
                        "picture_link": lot_details["Thumbnail"],
                        "property_description": inner_details["Description"],
                        "property_link": url.replace("page-data.json", "").replace("/page-data", ""),
                        "address": full_address,
                        "postal_code": lot_details["PostCode"],
                        "number_of_bedrooms": inner_details["Bedrooms"],
                        "property_type": inner_details["PropertyType"],
                        "tenure": inner_details["TenureType"],
                        "auction_datetime": auction_date,
                        "auction_venue": None,
                        "source": "auctionhouselondon.co.uk",
                    }
                    HouseAuction.sv_upd_result(data_hash)
                except BaseException as be:
                    save_error_report(be, __file__)
                    # _traceback = get_traceback()
                    # if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                    #     error_report.count = error_report.count + 1
                    #     error_report.save()
                    # else:
                    #     ErrorReport.objects.create(file_name="auctionhouselondon.py", error=str(be),
                    #                                trace_back=_traceback)

    def scraper(self):
        response = self.connect_to(self.URL)
        data = load_json(response.content)
        self.parser(data)


def run():
    AuctionHouseLondon().scraper()
