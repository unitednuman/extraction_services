from datetime import timedelta

import dateparser
import requests
from lxml import html
from lxml.html import HtmlElement

from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction


def parse_property(url, imagelink):
    try:
        response = requests.get(url, timeout=10)
        result: HtmlElement = html.fromstring(response.content)
        fix_br_tag_issue(result)
        auction_closing_els = result.xpath("//input[@id='_seconds-to-closing']")
        if not auction_closing_els:
            return
        secs_to_auction_close = int(auction_closing_els[0].attrib["value"])
        secs_to_auction_start = int(result.xpath("//input[@id='_seconds-to-auction-start']")[0].attrib["value"])
        if secs_to_auction_close <= 0:
            return
        try:
            close_datetime_el = result.xpath("//div[@class='auction-date-bar']")[0]
        except IndexError:
            save_error_report(
                Exception(
                    "Unable to get closing date",
                    dict(secs_to_auction_close=secs_to_auction_close, secs_to_auction_start=secs_to_auction_start),
                ),
                secondary_error=True,
            )
            return
        close_datetime_txt = (
            close_datetime_el.text_content().replace("Auction Date", "").replace("Closing Time", "").strip()
        )
        close_datetime = dateparser.parse(close_datetime_txt)
        diff = secs_to_auction_close - secs_to_auction_start
        auction_datetime = close_datetime - timedelta(seconds=diff)
        price, currency_symbol = prepare_price(
            result.xpath("//div[contains(@class, 'price')]//p[.!='']")[0].text.replace("Invited Opening Bid", "")
        )

        address = result.xpath("//h2[contains(@class,'m-0 order-1 order-lg-0')]")[0].text
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='property-page']")[0].text_content().strip().replace("\n", " ")
        property_type = get_property_type(result.xpath("//div[contains(@class, 'property-type')]")[0].text.strip())
        if property_type == "other":
            property_type = get_property_type(description)
        tenure_str = get_text(
            result,
            0,
            "//h3[contains(text(),'Tenure')]//parent::div//following-sibling::div//p",
        )
        tenure = get_tenure(tenure_str)
        if tenure is None:
            tenure = get_tenure(description)
        no_of_beds = get_bedroom(description)
        data_hash = {
            "price": price,
            "currency_type": currency_symbol,
            "picture_link": imagelink,
            "property_description": description,
            "property_link": response.url,
            "address": address,
            "postal_code": postal_code,
            "property_type": property_type,
            "tenure": tenure,
            "auction_datetime": auction_datetime,
            "auction_venue": "",
            "source": "bidx1.com",
            "number_of_bedrooms": no_of_beds,
        }
        HouseAuction.sv_upd_result(data_hash)
    except BaseException as be:
        save_error_report(be, __file__)


def run():
    try:
        temp_url = "https://bidx1.com/en/united-kingdom?page={}"
        page = 1
        while True:
            url = temp_url.format(page)
            base_url = "https://bidx1.com"
            # base_url = "https://bidx1.com/en/united-kingdom?region=2&maxprice=&division="
            response = requests.request("GET", url, timeout=10)
            result = html.fromstring(response.content)
            fix_br_tag_issue(result)
            for property in result.xpath('//div[@class="card property-card flex-fill"]'):
                try:
                    url = base_url + property.xpath(".//a")[0].attrib["href"]

                    imagelink = result.xpath(".//div[@class='property-card__image-container']//img")[0].attrib["src"]
                    parse_property(url, imagelink)
                except BaseException as be:
                    save_error_report(be, __file__)
            try:
                page_check = result.xpath("//a[@class='page-link no-hover-shadow']")[-1].text_content()
            except:
                page_check = ""
            if "next" in page_check:
                break
            page += 1
    except BaseException as be:
        save_error_report(be, __file__)
