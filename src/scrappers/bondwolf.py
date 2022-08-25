import time
from lxml import html
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction
from playwright.sync_api import sync_playwright

start_url = "https://www.bondwolfe.com/auctions/properties/?location=&minprice=&maxprice=&type="


def parse_property(page, url):
    page.goto(url)
    time.sleep(5)
    response = page.content()
    result = html.fromstring(response)
    fix_br_tag_issue(result)
    auction_time = parse_auction_date(
        result.xpath("//div[@class='AuctionDetails-datetime']//h2")[0].text_content().strip())
    description = result.xpath("//h4[contains(text(), 'Property Description')]//parent::div")[0].text_content().strip()

    tenure_str = get_text(result, 0, "//h4[contains(text(), 'Tenure')]//parent::div")
    tenure = get_tenure(tenure_str)
    price_text = result.xpath("//h2[@class='h1 mb-1 PropertyHeader-price-value']")[0].text_content().strip()
    price, currency = prepare_price(price_text)
    address, *other_details = result.xpath("//div[@class='PropertyHeader-description pr-lg-5']")[0].text_content().strip().split('\n')
    postal_code = parse_postal_code(address, __file__)
    if other_details:
        detail = other_details[0]
        if 'bedroom' in detail and (match := re.search(r"(\d+)\sbedroom", detail, flags=re.I)):
            number_of_bedrooms = int(match.group(1))
        else:
            number_of_bedrooms = None
        property_type = get_property_type(detail)
    else:
        property_type = None
        number_of_bedrooms = None
    tenure,property_type,number_of_bedrooms=get_beds_type_tenure(tenure,property_type,number_of_bedrooms,description)
    imagelink = result.xpath("//div[@class='slick-list draggable']//img")[0].attrib['src']
    propertyLink = page.url
    venue = get_text(result, 0, "//div[@class='AuctionDetails-location']//p")
    data_hash = {
        # "_id": details["version"]["allsop_auctionid"],
        "price": price,
        "currency_type": currency,
        "picture_link": imagelink,
        "property_description": description,
        "property_link": propertyLink,
        "address": address,
        "postal_code": postal_code,
        "auction_datetime": auction_time,
        "auction_venue": venue,
        "source": "bondwolfe.com",
        "property_type": property_type,
        "number_of_bedrooms": number_of_bedrooms,
        "tenure": tenure,
    }
    HouseAuction.sv_upd_result(data_hash)


def start():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(start_url)
        page.locator("//label[@for='postPerPage5']").first.click()
        time.sleep(3)
        result = html.fromstring(page.content())
        fix_br_tag_issue(result)
        if result.xpath("//h3[contains(text(), 'Properties coming soon.')]"):
            print("No Properties Found")
            browser.close()
            return
        for property in result.xpath("//a[@class='PropertyCard']"):
            try:
                url = property.xpath('.')[0].attrib['href']
                parse_property(page, url)
            except BaseException as be:
                save_error_report(be, __file__)


def run():
    start()
