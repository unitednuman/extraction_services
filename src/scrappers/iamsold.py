import json
from lxml import html
import requests
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport


def parse_properties(html_content):
    for property in html_content.xpath("//div[@id='properties-container']//div[@class='properties-preview']"):
        try:
            venue = get_text(property, 0, ".//div[@class='properties-preview-status']//span")
            pictureLink = get_attrib(property, ".//div[@class='properties-preview-image']//img", 0, "src")

            price_str = get_text(property, 1, ".//div[@class='properties-preview-content-price']//span")
            price, currency_symbol = prepare_price(price_str)
            address = get_text(property, 0, ".//span[@class='properties-preview-content-details-address']")
            postalcode = get_text(property, 0,
                                  ".//span[@class='properties-preview-content-details-address details-address-postcode']")

            numberOfBedrooms = get_text(property, 0, ".//span[contains(text(), 'Bedroom')]")
            detailed_page_url = get_attrib(property, ".//a", 0, 'href')
            if detailed_page_url:
                propertyLink = "https://www.iamsold.co.uk" + detailed_page_url
                response = requests.get(propertyLink)
                result = html.fromstring(response.content)
                end_time = get_attrib(result, "//span[@class='end_time_auto']", 0, "data-time-end")
                auction_datetime = parse_auction_date(end_time)
                propertyDescription = result.xpath("//div[@class='inner-properties-content']")[0].text_content()
            else:
                continue
            data_hash = {
                "price": price,
                "currency_type": currency_symbol,
                "picture_link": pictureLink,
                "property_description": propertyDescription,
                "property_link": response.url,
                "address": address,
                "number_of_bedrooms": numberOfBedrooms,
                "auction_datetime": auction_datetime,
                "auction_venue": venue,
                "source": "iamsold.co.uk"
            }
            if house_auction := HouseAuction.objects.filter(property_link=response.url):
                house_auction.update(**data_hash)
            else:
                HouseAuction.objects.create(**data_hash)
        except BaseException as be:
            _traceback = get_traceback()
            if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                error_report.count = error_report.count + 1
                error_report.save()
            else:
                ErrorReport.objects.create(file_name="iamsold.py", error=str(be), trace_back=_traceback)


def run():
    url = "https://www.iamsold.co.uk/auction/properties"

    payload = {'region': '',
               'offline': 'all',
               'range': 'Search Radius',
               'minprice': 'Min Price',
               'maxprice': 'Max Price',
               'residential_type': 'Property Type',
               'minbed': 'Min Bedrooms',
               'maxbed': 'Max Bedrooms',
               'location': '',
               'dateAdded': 'Date Added',
               'bidPrice': 'Bid Price',
               'context': 'generic',
               'pageNumber': '1'}
    response = requests.request("POST", url, data=payload)
    results = json.loads(response.content)
    content = html.fromstring(results['properties'])
    parse_properties(content)
    total_pages = int(int(results['totalProperties']) / 12)
    for page in range(2, total_pages + 1):
        payload['pageNumber'] = str(page)
        response = requests.request("POST", url, data=payload)
        results = json.loads(response.content)
        content = html.fromstring(results['properties'])
        parse_properties(content)
