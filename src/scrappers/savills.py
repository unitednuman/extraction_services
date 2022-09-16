import requests
from scrappers.traceback import get_traceback, save_error_report
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction, ErrorReport

catalogue_url = "https://auctions.savills.co.uk/index.php?option=com_calendar&format=json&task=upcoming.getAuctions"

payload = "current_page=1&auctions_per_page=100"


def parse_property(auction_id, lot_id, auction_date, venue):
    proccess_lot_url = "https://auctions.savills.co.uk/index.php?option=com_bidding&format=json&task=commission.processLot"
    processlot_payload = {'auction_id': auction_id,
                          'lot_id': lot_id}
    url = "https://auctions.savills.co.uk/"
    response = requests.post(proccess_lot_url, data=processlot_payload, timeout=10)
    json_data = load_json(response.content)
    description = json_data['lot']['description'] + "\n" + json_data['lot']['key_features'] + "\n" + json_data['lot'][
        'accommodation']
    pictureLink = url + json_data['lot']['images'][0]['large_image']
    price = json_data['lot']['low_estimate']
    tenure = get_tenure(json_data['lot']['tenure'])
    address = json_data['lot']['name']
    postal_code = parse_postal_code(address, __file__)
    auction_datetime = auction_date
    currency = 'GBP'
    propertyLink = url + json_data['lot']['link']
    property_type = number_of_bedrooms = None

    tenure, property_type, number_of_bedrooms = get_beds_type_tenure(tenure, property_type, number_of_bedrooms,
                                                                     description)

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
        "property_type": property_type,
        "number_of_bedrooms": number_of_bedrooms,
        "auction_venue": venue,
        "source": "auctions.savills.co.uk"
    }
    HouseAuction.sv_upd_result(data_hash)

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
    response = requests.post(lot_url, data=lots_payload, timeout=10)
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
                save_error_report(be, __file__)

        offset += 100
        lots_payload['lot_offset'] = str(offset)


def run():
    response = requests.request("POST", catalogue_url, data=payload, timeout=10)
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
