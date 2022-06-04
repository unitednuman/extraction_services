import requests
import json
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport

catalogue_url = "https://auctions.savills.co.uk/index.php?option=com_calendar&format=json&task=upcoming.getAuctions"

payload = "current_page=1&auctions_per_page=100"
headers = {
    'Content-Type': 'text/plain',
    'Cookie': '58beab80ac854423b2c304b17fc8ba11=725df13cde9cba55097c6b79067ae90f'
}


def parse_property(auction_id, lot_id, auction_date, venue):
    proccess_lot_url = "https://auctions.savills.co.uk/index.php?option=com_bidding&format=json&task=commission.processLot"
    payload = {'auction_id': auction_id,
               'lot_id': lot_id}
    domain = "https://auctions.savills.co.uk/"
    response = requests.post(proccess_lot_url, data=payload)
    json_data = json.loads(response.content)
    description = json_data['lot']['description']
    pictureLink = domain + json_data['lot']['images'][0]['large_image']
    price = json_data['lot']['low_estimate']
    tenure = json_data['lot']['tenure']
    address = json_data['lot']['name']
    postal_code = address.split(',')[-1]
    auction_date = auction_date
    currency = 'GBP'
    propertyLink = domain + json_data['lot']['link']
    data_hash = {
        # "_id": details["version"]["allsop_auctionid"],
        "price": price,
        "currency_type": currency,  # TODO: Add currency type
        "picture_link": pictureLink,
        "property_description": description,
        "property_link": propertyLink,
        "address": address,
        "postal_code": postal_code,
        "tenure": tenure,
        "auction_datetime": auction_date,  # TODO : combine date and hour
        # "auction_hour": auc_hours,  combine it with auction_date_time
        "auction_venue": venue,
        "source": domain
    }
    if house_auction := HouseAuction.objects.filter(property_link=propertyLink):
        house_auction.update(**data_hash)
    else:
        HouseAuction.objects.create(**data_hash)

    # print(description, pictureLink, price, tenure, address, postal_code, auction_date, currency, domain, propertyLink)
    print(propertyLink, venue)


def parse_lot(auction_id, auction_date, venue):
    lot_url = "https://auctions.savills.co.uk/index.php?option=com_bidding&format=json&task=commission.getLots"
    payload = {'auction_id': auction_id,
               'lot_offset': '0',
               'lots_per_page': '100',
               'search': '',
               'property_type': '',
               'sort_by': ''}
    response = requests.post(lot_url, data=payload)
    offset = 0
    json_data = json.loads(response.content)
    total_pages = int(int(json_data['total_lots']) / 100)
    print("Total Pages: ", total_pages)
    for page in range(total_pages + 1):
        print("Page Number: ", page)
        for lot in json_data['lots']:
            lot_id = lot["id"]
            parse_property(auction_id, lot_id, auction_date, venue)
        offset += 100
        payload['lot_offset'] = str(offset)


def run():
    response = requests.request("POST", catalogue_url, headers=headers, data=payload)
    data = json.loads(response.content)
    count = 0
    for auction in data['auctions']:
        if count >= 2:
            break
        try:
            auction_id = auction['id']
            auction_date = auction['auction_date'] + " " + auction['auction_time']
            venue = auction['location']['address1'] + " " + auction['location']['postcode']
            parse_lot(auction_id, auction_date, venue)
            count += 1
        except BaseException as be:
            _traceback = get_traceback()
            if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                error_report.count = error_report.count + 1
                error_report.save()
            else:
                ErrorReport.objects.create(file_name="savills.py", error=str(be), trace_back=_traceback)
