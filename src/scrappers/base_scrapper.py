import dateparser
from price_parser import Price


def get_text(node, index, xpath):
    try:
        return node.xpath(xpath)[index].text
    except Exception as e:
        print("attribute finding error", e, xpath)
        return ''


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
        auction_date = dateparser.parse(auction_date)
        return auction_date
    except Exception as e:
        raise ValueError("Unable to parse auction date", e)
