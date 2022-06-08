from wsgiref import headers
import requests
from lxml import html
import dateparser
from price_parser import parse_price
from extraction_services.models import HouseAuction

class AuctionHouse:
    DOMAIN = 'https://www.auctionhouse.co.uk'
    URL = 'https://www.auctionhouse.co.uk/auction/search-results?searchType=0'

    def __init__(self):
        pass

    def connect_to(self, url):
        # print(url)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Origin': 'https://www.auctionhouse.co.uk',
            'Referer': 'https://www.auctionhouse.co.uk/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36',
        }
        res = requests.get(url, headers=headers, data={})
        # print(f"------ Request Response : {res.status_code} --------")
        return res

    def parser(self, response):
        for lot_detail in response.xpath("//div[@class='col-sm-12 col-md-8 col-lg-6 text-center lot-search-result']"):
            if "Sold" in lot_detail.xpath(".//div[@class='lot-search-wrapper grid-item']//div//text()")[4]:
                continue
            lot_link = self.DOMAIN + lot_detail.xpath(".//a//@href")[0]
            res = self.connect_to(lot_link)
            parsed_content = html.fromstring(res.content)
            price = parse_price(parsed_content.xpath("//h4[@class='guideprice']//text()")[0]).amount_float
            currency = parse_price(parsed_content.xpath("//h4[@class='guideprice']//text()")[0]).currency
            full_address = parsed_content.xpath("//div[@id='lotnav']//p//text()")[0]
            url = res.url
            lot_id = url.split("/")[-1]
            thumbnail = self.DOMAIN + parsed_content.xpath("//div[@class='item img-thumbnail-wrapper active']//img//@src")[0]
            bedrooms = [text for text in parsed_content.xpath("//div[@class='lot-info-right']//li//text()") if "Bedroom" in text][0].split()[0]
            tenure = [text for text in parsed_content.xpath("//div[@class='lot-info-right']//li") if "Tenure" in text.text_content()][0].text_content().split(":")[-1].strip()
            venue = [text for text in parsed_content.xpath("//p[@class='auction-info-header']") if "Venue" in text.text_content()][0].getnext().text_content().replace(',','').strip()
            auction_date = dateparser.parse(parsed_content.xpath("//div[@class='auction-date']//p")[-1].text_content() + " "+ parsed_content.xpath("//div[@class='auction-time']//p")[-1].text_content()).isoformat()
            data_hash = {}
            data_hash = {
                "_id": lot_id,
                "guidePrice": price,
                "currency": currency,
                "pictureLink": thumbnail,
                "propertyDescription": parsed_content.xpath("//div[@class='preline']")[0].text_content(),
                "propertyLink": url,
                "address": full_address,
                "postcode": full_address.split(",")[-1],
                "numberOfBedrooms": bedrooms,
                "propertyType": None,
                "tenure": tenure,
                "auction_datetime": auction_date,
                "auction_venue": venue,
                "domain": self.DOMAIN
            }
            if house_auction := HouseAuction.objects.filter(property_link=res.url):
                house_auction.update(**data_hash)
            else:
                HouseAuction.objects.create(**data_hash)
      

    def scraper(self):
        response = self.connect_to(self.URL)
        parsed_response = html.fromstring(response.content)
        item = []
        item = self.parser(parsed_response)


def run():
    AuctionHouse().scraper()
