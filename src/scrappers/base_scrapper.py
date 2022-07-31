import re
import dateparser
from price_parser import Price
import logging
import json
from json import JSONDecodeError
from scrappers.traceback import save_error_report

logging.basicConfig(format="%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s", level=logging.DEBUG)


def disable_other_loggers():
    for name in logging.root.manager.loggerDict:
        # print("logger", name)
        logging.getLogger(name).disabled = True


disable_other_loggers()
logger = logging.getLogger('scrapers')


def load_json(content):
    try:
        json_data = json.loads(content)
        return json_data
    except JSONDecodeError as ex:
        raise Exception(f"Unable to load JSON with content = {content}, with exception {ex}")


def get_text(node, index, xpath):
    try:
        return node.xpath(xpath)[index].text_content().strip()
    except Exception as e:
        logger.debug(f"could not find text with Xpath = {xpath}, with exception {e}")
        return None


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
        logger.debug(f"could not find Attribute with Xpath = {xpath}, with exception {e}")
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


def parse_postal_code(text, fn_for_error_report):
    try:
        return re.search(r"(\w+\s\w+)\s*$", text).group(1)
    except BaseException as be:
        be.args = be.args + (text,)
        save_error_report(be, fn_for_error_report)
        return None


property_types_re = re.compile(r"\b" + r"\b|\b".join([
    'end-of-terrace-house', 'land', 'terraced-house', 'flat', 'semi-detached-house', 'shop', 'cottage',
    'detached-house', 'apartment', 'detached-bungalow', 'commercial', 'bungalow', 'studio', 'terraced',
    'semi-detached', 'detached'
]) + r"\b", flags=re.I)


def get_property_type(text):
    if match := property_types_re.search(text):
        return match.group()
    return "other"


def fix_br_tag_issue(doc):
    for br in doc.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"
