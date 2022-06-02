from lxml import html
import requests
from scrappers.traceback import get_traceback
import dateparser
from extraction_services.models import HouseAuction, ErrorReport
from price_parser import Price

base_url = "https://www.sdlauctions.co.uk"


def get_text(node, index, xpath, raise_error=True):
    try:
        return node.xpath(xpath)[index].text_content()
    except Exception as e:
        if not raise_error:
            print("attribute finding error", e, xpath)
            return ''
        return ValueError(f"Unable to get text for {xpath}", e)


def get_attrib(node, xpath, index, attribute):
    try:
        return node.xpath(xpath)[index].attrib[attribute]
    except Exception as e:
        print("attribute finding error", e, attribute)
        return ''


def currency_iso_name(currency):
    symbols = {
        "£": "GBP",
        "$": "USD",
    }
    try:
        return symbols[currency]
    except:
        return "Currency Not Found"


def prepare_price(price):
    price_str = Price.fromstring(price)
    price = price_str.amount_float
    currency = price_str.currency
    currency = currency_iso_name(currency)
    return price, currency


def parse_auction_date(auction_date):
    try:
        auction_date = auction_date.strip().split('\t')[
            -1].strip()
        auction_date = dateparser.parse(auction_date)
        return auction_date
    except Exception as e:
        raise ValueError("Unable to parse auction date", e)


def parse_properties(results):
    for property in results.xpath("//div[@class='auction-card']//div[@class='auction-card--content']"):
        try:
            propertyLink = base_url + get_attrib(property, "a", 0, "href")
            numberOfBedrooms = get_text(property, 0, ".//i[@class='fa fa-bed']//following-sibling::span")
            address = get_text(property, 0, ".//li[@class='auction-card--contend-address']")
            if address:
                postcode = address.split(',')[-1]
            else:
                postcode = 0
            price = get_text(property, 0, ".//li[@class='auction-card--guide-price']//following-sibling::li")
            guidePrice = prepare_price(price)[0]
            currency = prepare_price(price)[1]
            auction_date = get_text(property, 0, "//b[contains(text(), 'Auction date:')]//parent::li")
            auction_date = parse_auction_date(auction_date)
            response = requests.get(propertyLink)
            result = html.fromstring(response.content)
            propertyDescription = get_text(result, 0,
                                           "//div[contains(text(),'Property Description:')]//following-sibling::p")
            tenure = get_text(result, 0, "//div[contains(text(),'Tenure: ')]//following-sibling::p")
            pictureLink = get_attrib(result, "//a[@data-lightbox='property-image']//img", 1, "src")
            data_hash = {
                # "_id": details["version"]["allsop_auctionid"],
                "price": guidePrice,
                "currency_type": currency,
                "picture_link": pictureLink,
                "property_description": propertyDescription,
                "property_link": propertyLink,
                "address": address,
                "postal_code": postcode,
                "number_of_bedrooms": numberOfBedrooms,
                "auction_datetime": auction_date,  # TODO : combine date and hour
                # "auction_hour": auc_hours,  combine it with auction_date_time
                "tenure": tenure,
                "source": base_url
            }
            if house_auction := HouseAuction.objects.filter(property_link=propertyLink):
                house_auction.update(**data_hash)
            else:
                HouseAuction.objects.create(**data_hash)
        except BaseException as be:
            _traceback = get_traceback()
            if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                error_report.count = error_report.count + 1
                error_report.save()
            else:
                ErrorReport.objects.create(file_name="sdlauctions.py", error=str(be), trace_back=_traceback)


def parse_auctions(results):
    for auction in results.xpath("//div[@class='events-list']//div[@class='btn-flex-holder']"):
        auction_id = int(auction.xpath("a")[0].attrib['href'].split('/')[2])
        url = "https://www.sdlauctions.co.uk/wp-content/themes/sdl-auctions/library/property-functions.php"
        payload = {'func': 'ajaxProp',
                   'data': f'location=&minBeds=&maxBeds=&minPrice=&maxPrice=&lat=&lng=&bounds=&tempType=auction&search=1&radius=3&auctionId={auction_id}&include%5B%5D=&limit=All&page=1&order=Lot Number&oos=0'}
        response = requests.post(url, data=payload)
        results = html.fromstring(response.content)
        parse_properties(results)


def run():
    response = requests.get("https://www.sdlauctions.co.uk/property-auctions/auction-events/")
    results = html.fromstring(response.content)
    parse_auctions(results)
