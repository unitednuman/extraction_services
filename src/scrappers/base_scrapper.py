import dateparser
from price_parser import Price
import logging
import json
from json import JSONDecodeError


def load_json(content):
    try:
        json_data = json.loads(content)
        return json_data
    except JSONDecodeError as ex:
        raise Exception(f"Unable to load JSON with content = {content}, with exception {ex}")


def get_text(node, index, xpath):
    try:
        return node.xpath(xpath)[index].text
    except Exception as e:
        logging.debug(f"could not find text with Xpath = {xpath}, with exception {e}")
        return ''


def get_tenure(tenure_str):
    if tenure_str is None:
        return ""
    tenure_str = tenure_str.lower()
    if 'freehold' in tenure_str:
        return "Freehold"
    elif 'leasehold' in tenure_str:
        return 'Leasehold'
    else:
        return ""


def get_attrib(node, xpath, index, attribute):
    try:
        return node.xpath(xpath)[index].attrib[attribute]
    except Exception as e:
        logging.debug(f"could not find Attribute with Xpath = {xpath}, with exception {e}")
        return ''


def currency_iso_name(currency):
    symbols = {
        "£": "GBP",
        "$": "USD",
    }
    try:
        return symbols[currency]
    except:
        raise Exception(f"Currency symbol \"{currency}\" not matching with available ones.")


def prepare_price(price):
    price_obj = Price.fromstring(price)
    price = price_obj.amount_float
    currency = price_obj.currency
    currency = currency_iso_name(currency)
    return price, currency


def parse_auction_date(auction_date_str):
    auction_date = dateparser.parse(auction_date_str)
    if auction_date is not None:
        return auction_date
    raise Exception(f"Unable to parse date from \"{auction_date}\" string")
