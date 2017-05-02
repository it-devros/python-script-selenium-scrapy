import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

from selenium import webdriver
from lxml import html

class SajeSpider(scrapy.Spider):
    name = "saje"

    domain = "https://www.la-z-boy.com"
    # start_urls = ["https://www.saje.com/store-locator/"]

    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")

    def start_requests(self):
        self.driver.get("https://www.saje.com/store-locator/")
        
        source = self.driver.page_source.encode("utf8")
        self.driver.close()

        tree = html.fromstring(source)

        stores = tree.xpath("//table[@id='store-location-results']//tbody//tr")
        requests = []

        for store in stores:
            store_name = store.xpath(".//a[@class='store-click store-name']/text()")[0]
            url = store.xpath(".//a[@class='store-click store-name']/@href")[0]
            address = store.xpath(".//td[@class='store-address']//div/text()")
            address_token = address[1]

            city = address[1].split(",")[0].strip()
            temp = address[1].split(",")[1].strip().split(" ")
            if address[2].strip() == "Canada":
                state = " ".join(temp[:-2])
                zip_code = " ".join(temp[-2:])
            else:
                state = " ".join(temp[:-1])
                zip_code = temp[-1]

            request = scrapy.Request(url=self.domain + url, callback=self.parse)
            request.meta["store_name"] = store_name.replace("\n", "").strip()
            request.meta["address"] = address[0].strip()
            request.meta["country"] = address[2].strip()
            request.meta["state"] = state
            request.meta["city"] = city
            request.meta["zip_code"] = zip_code
            request.meta["phone_number"] = store.xpath(".//td[@class='store-phone']//a/text()")[0]
            try:
                request.meta["comming_soon"] = store.xpath(".//div[@class='store-hours']/text()")[0].replace("\n", "").strip()
            except:
                request.meta["comming_soon"] = ""
            
            requests.append(request)

        for req in requests:
            yield req
        # yield scrapy.Request(url="https://www.saje.com/store-locator/", headers=self.headers, callback=self.parse)

    def parse(self, response):
        # get open hours
        if response.meta["comming_soon"] == "":
            open_hours = []
            open_days = response.xpath("//div[@class='store-hours']//p[@class='day']/text()")
            open_hrs = response.xpath("//div[@class='store-hours']//p[@class='hour']/text()")

            for index in range(0, len(open_days)):
                open_hours.append(open_days[index].extract()+open_hrs[index].extract())
            open_hours = "; ".join(open_hours)
        else:
            open_hours = ""

        item = ChainItem()
        item['store_name'] = response.meta["store_name"]
        item['store_number'] = ""
        item['address'] = response.meta["address"]
        item['phone_number'] = response.meta["phone_number"]
        item['city'] = response.meta["city"]
        item['state'] = response.meta["state"]
        item['zip_code'] = response.meta["zip_code"]
        item['country'] = response.meta["country"]
        item['latitude'] = ""
        item['longitude'] = ""
        item['store_hours'] = open_hours
        #item['store_type'] = info_json["@type"]
        item['other_fields'] = ""
        item['coming_soon'] = response.meta["comming_soon"]

        yield item

    def validate(self, xpath_obj):
        try:
            return xpath_obj.extract_first().strip()
        except:
            return ""

