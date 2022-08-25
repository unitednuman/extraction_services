import inspect
import os
import re
from datetime import datetime
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


def get_text(nodes, index, xpath):
    try:
        return nodes.xpath(xpath)[index].text_content().strip()
    except Exception as e:
        e.args += (xpath,)
        try:
            filenames = ", ".join({os.path.basename(s.filename) for s in inspect.stack() if r"scrappers" in s.filename})
        except Exception as ex:
            logging.debug(f"error while fetching filenames: {ex}")
            filenames = ""
        save_error_report(e, filenames, secondary_error=True)
        logger.debug(f"could not find text with Xpath = {xpath}, with exception {e}")
        return None

leashold_re = re.compile(r"\b" + r"\b|\b".join(
    map(lambda v: v.replace(' ', r'[\s -]+'),['currently let','leasehold','tenant-in-situ','tenanted','tenant','tenancy'])
    ) + r"\b", flags=re.I)

freehold_re = re.compile(r"\b" + r"\b|\b".join(
    map(lambda v: v.replace(' ', r'[\s -]+'),['freehold','A vacant three bedroom end-terrace'])
    ) + r"\b", flags=re.I)


def get_tenure(tenure_str):
    if tenure_str is None:
        return None
    tenure_str = tenure_str.lower()
    if freehold_re.search(tenure_str):
        return "Freehold"
    elif leashold_re.search(tenure_str):
        return 'Leasehold'
    
    else:
        return None


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


def parse_auction_date(auction_date_str, **kwargs):
    auction_date = dateparser.parse(auction_date_str, **kwargs)
    if auction_date is not None:
        return auction_date
    raise Exception(f"Unable to parse date from \"{auction_date_str}\" string")

def parse_uk_date(text):
    match=re.search(r"(\d+)/(\d+)/(\d+)", text)
    if not match:
        raise Exception(f"Unable to parse date from \"{text}\" string")
    dt = datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))
    return dt
def parse_postal_code(text, fn_for_error_report):
    try:
        return re.search(r"(\w+\s\w+)\s*$", text).group(1)
    except BaseException as be:
        be.args = be.args + (text,)
        save_error_report(be, fn_for_error_report)
        return None


property_types_re = re.compile(r"\b" + r"\b|\b".join(map(lambda v: v.replace(' ', r'[\s -]+'), ['commercial',
    'end of terrace house', 'land', 'terraced house', 'flat', 'semi detached house', 'shop',
    'cottage',
    'detached house', 'apartment', 'detached bungalow',  'bungalow', 'studio', 'terraced',
    'semi detached', 'detached', 'end terrace', 'mid terrace', 'bungalow', 'house semi detached',
    'house end of terrace','end of terrace'
])) + r"\b", flags=re.I)
property_types_map = {
    'house semi detached': 'semi detached house',
    'house end of terrace': 'end of terrace house',
    'end of terrace': 'end of terrace house'
}


def get_property_type(text):
    if match := property_types_re.search(text):
        property_type = match.group().replace('-', ' ').lower()
        if property_type in property_types_map:
            property_type = property_types_map[property_type]
        return property_type
    return "other"


def fix_br_tag_issue(doc):
    for br in doc.xpath("*//br"):
        br.tail = "\n" + br.tail if br.tail else "\n"


def convert_words_to_integer(word):
    numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
               "eight": 8, "nine": 9, "ten": 10,"double":2}
    try:
        return numbers[word.strip().lower()]
    except BaseException as be:
        try:
            return int(word.strip())
        except BaseException as de:
            de.args = de.args + be.args + (word,)
            save_error_report(de, __file__, secondary_error=True)
    return None


def get_bedroom(text):
    numRooms = re.search(r"(one|two|three|four|five|six|seven|eight|nine|ten|double)\+? *(?:double +)?-?bed(?:room)?s?|bed(?:room)?s?:? *(\d+\+?)", text, re.IGNORECASE)
    if (numRooms):
        if (numRooms.group(1) is not None):
            return convert_words_to_integer(numRooms.group(1).strip())
        elif (numRooms.group(2) is not None):
            return int(numRooms.group(2))
    return None


def get_beds_type_tenure(tenure,property_type,no_of_beds,description):
    if tenure is None:
        tenure= get_tenure(description)
    if property_type:
        property_type_temp=get_property_type(property_type)
        if property_type_temp=="other":
            property_type_temp=get_property_type(description)
        if property_type_temp!="other":
            property_type=property_type_temp
    else:
        property_type_temp=get_property_type(description)
        if property_type_temp!="other":
            property_type=property_type_temp
        if property_type is None:
            property_type="other"
    if no_of_beds is None:
        no_of_beds=get_bedroom(description)
    return tenure,property_type,no_of_beds





# def get_bedroom(text):
#     no_of_beds=0
#     pattern = re.compile(r'(1|2|3|4|5|6|7|8|9|10|one|two|three|four|five|six|seven|eight|nine|ten|double)\+? *(?:double +)?-?bed(?:room)?s?|bed(?:room)?s?:? *(\d+\+?)', re.IGNORECASE)
#     for numRooms in pattern.finditer(text): 
#         if (numRooms.group(1)):
#             no_of_beds=no_of_beds+convert_words_to_integer(numRooms.group(1)) 
#         elif (numRooms.group(2)):
#             no_of_beds=no_of_beds+convert_words_to_integer(numRooms.group(2)) 
#     if no_of_beds:
#         return no_of_beds
#     return None
 