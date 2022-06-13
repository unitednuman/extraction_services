import requests
import json
from scrappers.traceback import get_traceback
from scrappers.base_scrapper import load_json
from extraction_services.models import HouseAuction, ErrorReport

catalogue_url = "https://auctions.savills.co.uk/index.php?option=com_calendar&format=json&task=upcoming.getAuctions"

payload = "current_page=1&auctions_per_page=100"


def parse_property(auction_id, lot_id, auction_date, venue):
    proccess_lot_url = "https://auctions.savills.co.uk/index.php?option=com_bidding&format=json&task=commission.processLot"
    processlot_payload = {'auction_id': auction_id,
                          'lot_id': lot_id}
    url = "https://auctions.savills.co.uk/"
    response = requests.post(proccess_lot_url, data=processlot_payload)
    json_data = load_json(response.content)
    description = json_data['lot']['description']
    pictureLink = url + json_data['lot']['images'][0]['large_image']
    price = json_data['lot']['low_estimate']
    tenure = json_data['lot']['tenure']
    address = json_data['lot']['name']
    postal_code = address.split(',')[-1]
    auction_datetime = auction_date
    currency = 'GBP'
    propertyLink = url + json_data['lot']['link']
    data_hash = {
        "price": price,
        "currency_type": currency,
        "picture_link": pictureLink,
        "property_description": description,
        "property_link": propertyLink,
        "address": address,
        "postal_code": postal_code,
        "tenure": tenure,
        "auction_datetime": auction_datetime,
        "auction_venue": venue,
        "source": "autions.savills.co.uk"
    }
    if house_auction := HouseAuction.objects.filter(property_link=propertyLink):
        house_auction.update(**data_hash)
    else:
        HouseAuction.objects.create(**data_hash)

    # print(description, pictureLink, price, tenure, address, postal_code, auction_date, currency, domain, propertyLink)
    # print(propertyLink, venue)


def parse_lot(auction_id, auction_date, venue):
    lot_url = "https://auctions.savills.co.uk/index.php?option=com_bidding&format=json&task=commission.getLots"
    lots_payload = {'auction_id': auction_id,
                    'lot_offset': '0',
                    'lots_per_page': '100',
                    'search': '',
                    'property_type': '',
                    'sort_by': ''}
    response = requests.post(lot_url, data=lots_payload)
    offset = 0
    json_data = load_json(response.content)
    total_pages = int(int(json_data['total_lots']) / 100)
    # print("Total Pages: ", total_pages + 1)
    for page in range(total_pages + 1):
        # print("Page Number: ", page + 1)
        for lot in json_data['lots']:
            try:
                lot_id = lot["id"]
                parse_property(auction_id, lot_id, auction_date, venue)
            except BaseException as be:
                _traceback = get_traceback()
                if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                    error_report.count = error_report.count + 1
                    error_report.save()
                else:
                    ErrorReport.objects.create(file_name="savills.py", error=str(be), trace_back=_traceback)

        offset += 100
        lots_payload['lot_offset'] = str(offset)


def run():
    response = requests.request("POST", catalogue_url, data=payload)
    data = load_json(response.content)
    count = 0
    for auction in data['auctions']:
        if count >= 2:
            break
        auction_id = auction['id']
        auction_date = auction['auction_date'] + " " + auction['auction_time']
        venue = auction['location']['address1'] + " " + auction['location']['postcode']
        parse_lot(auction_id, auction_date, venue)
        count += 1
