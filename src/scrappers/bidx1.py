import requests
from lxml import html
from scrappers.base_scrapper import *
from scrappers.traceback import get_traceback
from extraction_services.models import HouseAuction, ErrorReport


def parse_property(url, auction_datetime, imagelink):
    response = requests.get(url)
    result = html.fromstring(response.content)
    # print(response.url)
    price = None
    currency_symbol = None
    try:
        price, currency_symbol = prepare_price(result.xpath(
            "//p[contains(text(), '£')] | //p[contains(text(), 'price')]")[
                                                   0].text.replace("Invited Opening Bid", ""))
    except Exception as e:
        print("Price not found", e)
    address = result.xpath("//h2[contains(@class,'m-0 order-1 order-lg-0')]")[0].text
    postal_code = address.split(",")[-1]
    description = result.xpath("//div[@id='property-page']")[0].text_content().strip().replace("\n", " ")
    propertyType = result.xpath("//div[contains(@class, 'property-type')]")[0].text.strip()
    tenure_str = get_text(result, 0,
                      "//h3[contains(text(),'Tenure')]//parent::div//following-sibling::div//p | //h3[contains(text(),'Tenancy')]//parent::div//following-sibling::div//p")
    tenure = get_tenure(tenure_str)
    data_hash = {
        "price": price,
        "currency_type": currency_symbol,
        "picture_link": imagelink,
        "property_description": description,
        "property_link": response.url,
        "address": address,
        "postal_code": postal_code,
        "property_type": propertyType,
        "tenure": tenure,
        "auction_datetime": auction_datetime,
        "auction_venue": "",
        "source": "bidx1.com"
    }
    if house_auction := HouseAuction.objects.filter(property_link=response.url):
        house_auction.update(**data_hash)
    else:
        HouseAuction.objects.create(**data_hash)


def run():
    temp_url = "https://bidx1.com/en/united-kingdom?page={}"
    page = 1
    while True:
        url = temp_url.format(page)
        base_url = "https://bidx1.com"
        response = requests.request("GET", url)
        result = html.fromstring(response.content)

        for property in result.xpath("//div[@class='card property-card  flex-fill']//a"):
            url = base_url + property.attrib['href']
            try:
                auction_datetime = parse_auction_date(
                    result.xpath(
                        "//div[@class='sale-entity-status-label sale-entity-status-label--bidding-to-be-opened']")[
                        0].text.replace("Bidding Opens at", "").strip())
            except:
                auction_datetime = None
            imagelink = result.xpath("//div[@class='property-card__image-container']//img")[0].attrib['src']
            parse_property(url, auction_datetime, imagelink)
        try:
            page_check = result.xpath("//a[@class='page-link no-hover-shadow']")[-1].text_content()
        except:
            page_check = ""
        if 'next' in page_check:
            break
        page += 1
