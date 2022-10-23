import time
from lxml import html
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction

start_url = "https://www.networkauctions.co.uk/network-auctions-catalogues/"


def parse_property(page, url, price, currency, auction_img, auction_datetime_new):
    page.goto(url)
    time.sleep(5)
    response = page.content()
    result = html.fromstring(response)
    fix_br_tag_issue(result)

    description = (
        page.locator("xpath=(//div[@class='twelve fluid columns'])[1]")
        .inner_text()
        .replace("< Back to Lot ListNext Lot >Lot\n", "")
        .replace("< Back to Lot ListNext Lot >", "")
        .replace("< Previous Lot", "")
        .replace("Next Lot >", "")
        .strip()
    )
    tenure_nodes = result.xpath("//div[contains(translate(text(), 'TENURE', 'tenure'), 'tenure')]/following-sibling::p")
    tenure = None
    if tenure_nodes:
        tenure = get_tenure(tenure_nodes[0].text_content().strip())
    if tenure is None:
        tenure = get_tenure(description)
    address = result.xpath("//div[@class='address']")[0].text_content().strip()
    postal_code = parse_postal_code(address, __file__)
    number_of_bedrooms = get_bedroom(description)
    property_type = get_property_type(description)

    venue = "online auction"
    data_hash = {
        # "_id": details["version"]["allsop_auctionid"],
        "price": price,
        "currency_type": currency,
        "picture_link": auction_img,
        "property_description": description,
        "property_link": url,
        "address": address,
        "postal_code": postal_code,
        "auction_datetime": auction_datetime_new,
        "auction_venue": venue,
        "source": "networkauctions.co.uk",
        "property_type": property_type,
        "number_of_bedrooms": number_of_bedrooms,
        "tenure": tenure,
    }
    HouseAuction.sv_upd_result_thread(data_hash)


def start():
    with browser_context() as (page, browser):
        page.goto(start_url)
        time.sleep(3)
        page.locator("//button[contains(text(), 'Allow all')]").first.click()
        time.sleep(3)

        results = html.fromstring(page.content())
        fix_br_tag_issue(results)

        # for property in result.xpath("//table[@class='tableauctions']//a"):
        auction = results.xpath(".//iframe")
        page.goto(auction[0].attrib["src"])
        time.sleep(3)
        result = html.fromstring(page.content())
        fix_br_tag_issue(result)
        try:
            try:
                auction = result.xpath(".//table[@class='tableauctions']//a")[0]
            except:
                try:
                    auction = result.xpath("//table[@class='tableauctions']//a")[0]
                except:
                    pass
            url = "https://www.networkauctions.co.uk/online-auction-catalogues/" + auction.attrib["href"]
            auction_time = parse_auction_date(auction.text_content().strip())
            auction_datetime_new = datetime(auction_time.year, auction_time.day, auction_time.month, hour=10)
            page.goto(url)
            time.sleep(3)
            results = html.fromstring(page.content())
            fix_br_tag_issue(results)
            for auction in results.xpath(
                "//div[@style='margin-bottom:20px; background:#fafafa; border:solid 1px #efefef; padding:15px;']"
            ):
                guide_price = auction.xpath(".//p[@class='price']")[0].text_content().strip()
                price, currency = prepare_price(guide_price)
                auction_url = (
                    "https://www.networkauctions.co.uk/online-auction-catalogues/"
                    + auction.xpath(".//a[@class='button']")[0].attrib["href"]
                )
                auction_img = auction.xpath(".//img[@style='border-radius:2px;']")[0].attrib["src"]
                parse_property(page, auction_url, price, currency, auction_img, auction_datetime_new)
        except BaseException as be:
            save_error_report(be, __file__)


def run():
    start()
