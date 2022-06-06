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
        raise Exception(f"Currency symbol \"{currency}\" not matching with available ones.")


def prepare_price(price):
    price_obj = Price.fromstring(price)
    price = price_obj.amount_float
    currency = price_obj.currency
    currency = currency_iso_name(currency)
    return price, currency


def parse_auction_date(auction_date):
    auction_date = dateparser.parse(auction_date)
    if auction_date is not None:
        return auction_date
    raise Exception(f"Unable to parse date from \"{auction_date}\" string")