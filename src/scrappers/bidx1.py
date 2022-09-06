import requests
from lxml import html
from scrappers.base_scrapper import *
from extraction_services.models import HouseAuction


def parse_property(url, imagelink):
    try:
        response = requests.get(url, timeout=10)
        result = html.fromstring(response.content)
        fix_br_tag_issue(result)
        price = None
        currency_symbol = None
        try:
            price, currency_symbol = prepare_price(result.xpath(
                "//p[contains(text(), '£')] | //p[contains(text(), 'price')]")[
                                                    0].text.replace("Invited Opening Bid", ""))
        except Exception as e:
            save_error_report(e, __file__, secondary_error=True)
        address = result.xpath("//h2[contains(@class,'m-0 order-1 order-lg-0')]")[0].text
        postal_code = parse_postal_code(address, __file__)
        description = result.xpath("//div[@id='property-page']")[0].text_content().strip().replace("\n", " ")
        property_type = result.xpath("//div[contains(@class, 'property-type')]")[0].text.strip()
        tenure_str = get_text(result, 0,
                            "//h3[contains(text(),'Tenure')]//parent::div//following-sibling::div//p | //h3[contains(text(),'Tenancy')]//parent::div//following-sibling::div//p")
        tenure = get_tenure(tenure_str)
        no_of_beds=None
        tenure,property_type,no_of_beds=get_beds_type_tenure(tenure,property_type,no_of_beds,description)
        
        text=result.xpath("//div[@id='scheduled-closing-time']")[0].text_content().strip()
        
        auction_datetime_time = parse_auction_date(text.split(' time ')[1])
        auction_datetime=parse_uk_date(text)
        
        auction_datetime_new = datetime(auction_datetime.year, auction_datetime.month,auction_datetime.day, hour=auction_datetime_time.hour, minute=auction_datetime_time.minute)

        
        
        
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
            "auction_datetime": auction_datetime_new,
            "auction_venue": "",
            "source": "bidx1.com",
            "number_of_bedrooms": no_of_beds
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
            response = requests.request("GET", url, timeout=10)
            result = html.fromstring(response.content)
            fix_br_tag_issue(result)
            for property in result.xpath('//div[@class="card property-card flex-fill"]/a'):
                try:
                    url = base_url + property.attrib['href']
                    
                    imagelink = result.xpath("//div[@class='property-card__image-container']//img")[0].attrib['src']
                    parse_property(url, imagelink)
                except BaseException as be:
                    save_error_report(be, __file__)
            try:
                page_check = result.xpath("//a[@class='page-link no-hover-shadow']")[-1].text_content()
            except:
                page_check = ""
            if 'next' in page_check:
                break
            page += 1
    except BaseException as be:
        save_error_report(be, __file__)
