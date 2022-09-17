import requests
from lxml import html
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction


class AuctionHouse:
    DOMAIN = "https://www.auctionhouse.co.uk"
    URL = "https://www.auctionhouse.co.uk/auction/search-results?searchType=0"

    def __init__(self):
        pass

    def connect_to(self, url):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Origin": "https://www.auctionhouse.co.uk",
            "Referer": "https://www.auctionhouse.co.uk/",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
        }
        res = requests.get(url, headers=headers, data={}, timeout=10)
        # print(f"------ Request Response : {res.status_code} --------")
        return res

    def currency_iso_name(self, currency_symbol):
        symbols = {
            "£": "GBP",
            "$": "USD",
        }
        try:
            return symbols[currency_symbol]
        except:
            raise Exception(f'Currency symbol "{currency_symbol}" not matching with available ones.')

    def parser(self, response):
        for lot_detail in response.xpath("//div[@class='col-sm-12 col-md-8 col-lg-6 text-center lot-search-result']"):
            try:
                lot_types = "".join(lot_detail.xpath(".//div[@class='lot-search-wrapper grid-item']//div//text()"))
                if "Sold" in lot_types or "Postponed" in lot_types or "Withdrawn" in lot_types:
                    continue
                if "online.auctionhouse.co.uk" in lot_detail.xpath(".//a//@href")[0]:
                    continue
                lot_link = lot_detail.xpath(".//a//@href")[0]
                if not lot_link.startswith("https"):
                    lot_link = self.DOMAIN + lot_link
                res = self.connect_to(lot_link)
                parsed_content = html.fromstring(res.content)
                fix_br_tag_issue(parsed_content)
                price_str = parsed_content.xpath(
                    "//h4[@class='guideprice']//text() | //b[contains(text(),'Guide')]//text()"
                )[0]
                price, currency = prepare_price(price_str)
                # price = parse_price(parsed_content.xpath("//h4[@class='guideprice']//text() | //b[contains(text(),'Guide')]//text()")[0]).amount_float
                # currency = self.currency_iso_name(
                #     parse_price(parsed_content.xpath("//h4[@class='guideprice']//text()")[0]).currency)
                full_address = parsed_content.xpath("//div[@id='lotnav']//p//text()")[0]
                url = res.url
                lot_id = url.split("/")[-1]
                thumbnail = (
                    self.DOMAIN
                    + parsed_content.xpath(
                        "//div[@class='item img-thumbnail-wrapper active']//img//@src | //div[@id='carousel-lot-images']//img/@data-src"
                    )[0]
                )
                bedrooms_data = [
                    text
                    for text in parsed_content.xpath("//div[@class='lot-info-right']//li//text()")
                    if "Bedroom" in text
                ]
                bedrooms = bedrooms_data[0].split()[0] if bedrooms_data else None
                tenure_data = [
                    text
                    for text in parsed_content.xpath("//div[@class='lot-info-right']//li")
                    if "Tenure" in text.text_content()
                ]
                tenure = tenure_data[0].text_content().split(":")[-1].strip() if tenure_data else None
                if tenure:
                    tenure = get_tenure(tenure)
                venue_data = [
                    text
                    for text in parsed_content.xpath("//p[@class='auction-info-header']")
                    if "Venue" in text.text_content()
                ]
                venue = venue_data[0].getnext().text_content().replace(",", "").strip() if venue_data else None
                auction_datetime = None
                try:
                    auction_datetime = parse_auction_date(
                        parsed_content.xpath("//time[@class='end-date-time']")[0].text
                    )
                except:
                    pass
                if not auction_datetime:
                    auction_datetime = parse_auction_date(
                        parsed_content.xpath("//div[@class='auction-date']//p")[-1].text_content()
                        + " "
                        + parsed_content.xpath("//div[@class='auction-time']//p")[-1].text_content()
                    )
                property_description = (
                    parsed_content.xpath("//div[@class='preline'] | //div[@class='col-md-14 col-sm-13']")[0]
                    .text_content()
                    .strip()
                )
                property_type = None
                tenure, property_type, bedrooms = get_beds_type_tenure(
                    tenure, property_type, bedrooms, property_description
                )
                postcode = parse_postal_code(full_address, __file__)
                data_hash = {
                    # "_id": lot_id,
                    "price": price,
                    "currency_type": currency,
                    "picture_link": thumbnail,
                    "property_description": property_description,
                    "property_link": url,
                    "address": full_address,
                    "postal_code": postcode,
                    "number_of_bedrooms": bedrooms,
                    "property_type": property_type,
                    "tenure": tenure,
                    "auction_datetime": auction_datetime,
                    "auction_venue": venue,
                    "source": "auctionhouse.co.uk",
                }
                HouseAuction.sv_upd_result(data_hash)
            except BaseException as be:
                save_error_report(be, __file__)
                # _traceback = get_traceback()
                # if error_report := ErrorReport.objects.filter(trace_back=_traceback).first():
                #     error_report.count = error_report.count + 1
                #     error_report.save()
                # else:
                #     ErrorReport.objects.create(file_name="auctionhouse.py", error=str(be), trace_back=_traceback)

    def scraper(self):
        response = self.connect_to(self.URL)
        parsed_response = html.fromstring(response.content)
        fix_br_tag_issue(parsed_response)
        self.parser(parsed_response)


def run():
    AuctionHouse().scraper()
