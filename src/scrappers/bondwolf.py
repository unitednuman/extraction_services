import time
from datetime import timedelta

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
        result.xpath("//div[@class='AuctionDetails-datetime']//h2")[0].text_content().strip()
    )
    today_datetime = datetime.utcnow() + timedelta(hours=1)
    if auction_time < today_datetime:
        LoggerModel.debug(f"date has been passed. {auction_time = !s} {today_datetime = !s}")
        return
    description = result.xpath("//h4[contains(text(), 'Property Description')]//parent::div")[0].text_content().strip()
    tenure_str = get_text(result, 0, "//h4[contains(text(), 'Tenure')]//parent::div")
    tenure = get_tenure(tenure_str)
    if tenure is None:
        tenure = get_tenure(description)
    price_text = result.xpath("//h2[@class='h1 mb-1 PropertyHeader-price-value']")[0].text_content().strip()
    price, currency = prepare_price(price_text)
    address, *other_details = (
        result.xpath("//div[@class='PropertyHeader-description pr-lg-5']")[0].text_content().strip().split("\n")
    )
    postal_code = parse_postal_code(address, __file__)
    if other_details:
        detail = other_details[0]
        if "bedroom" in detail and (match := re.search(r"(\d+)\sbedroom", detail, flags=re.I)):
            number_of_bedrooms = int(match.group(1))
        else:
            number_of_bedrooms = None
        property_type = get_property_type(detail)
    else:
        property_type = None
        number_of_bedrooms = None
    if number_of_bedrooms is None:
        number_of_bedrooms = get_bedroom(description)
        if number_of_bedrooms is None and len(re.findall(r"\bbedroom\b", description, flags=re.I)) == 1:
            number_of_bedrooms = 1
    if property_type is None or property_type == "other":
        property_type = get_property_type(description)
    imagelink = result.xpath("//div[@class='slick-list draggable']//img")[0].attrib["src"]
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


def run():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(start_url)
            page.locator("//label[@for='postPerPage5']").first.click()
            time.sleep(3)
            result = html.fromstring(page.content())
            fix_br_tag_issue(result)
            if result.xpath("//h3[contains(text(), 'Properties coming soon.')]"):
                LoggerModel.debug("No Properties Found")
                return
            for property in result.xpath("//a[@class='PropertyCard']"):
                try:
                    url = property.xpath(".")[0].attrib["href"]
                    parse_property(page, url)
                except BaseException as be:
                    save_error_report(be, __file__)
        finally:
            browser.close()
