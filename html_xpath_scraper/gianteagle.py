import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import html

class GianteagleSpider(scrapy.Spider):
    name = "gianteagle"
    start_urls = ["https://www.gianteagle.com/Stores/"]
    
    def parse(self, response):
        total = int(response.xpath("//div[@class='pagerCounter']/text()").extract_first().split(" ")[-1])
        yield FormRequest(url="https://www.gianteagle.com/services/Listing/GetListItems",
                    formdata={ "type": "Store", "mainFilter": "", "filters": "[]", "start": "0", "count": str(total), "currentUrl": "https://www.gianteagle.com/Stores/", "query": "", "sortField": "Name", "saleField": "", "_callingUrl": "https://www.gianteagle.com/Stores/"},
                    callback=self.parse_store)
    
    def parse_store(self, response):
        stores = json.loads(json.loads(response.body))["items"]

        for store in stores:
            store = html.fromstring(store)
        
            item = ChainItem()
            item['store_name'] = store.xpath(".//div[@class='title slTitle']/a/text()")[0]
            item['store_number'] = store.xpath("./@data-prodid")[0]

            # parse address
            data = store.xpath(".//div[@class='storeInfo fLeft']/p/text()")
            data = [ pt.replace("\r\n", "").replace("\t", "") for pt in data if pt.replace("\r\n", "").replace("\t", "") != ""]

            tp = data[1].split(",")
            if len(tp) != 2:
                item['address2'] = data[1]
                tp = data[2].split(",")

            item['address'] = data[0]
            item['phone_number'] = "; ".join(data[2:-1])
            item['city'] = tp[0]
            temp = tp[1].strip().split(" ")
            item['state'] = temp[0]
            
            item['zip_code'] = temp[1] if len(temp) > 1 else ""
            item['country'] = "United States"
            item['latitude'] = store.xpath("./@data-lat")[0]
            item['longitude'] = store.xpath("./@data-lng")[0]
            item['store_hours'] = data[-1]
            #item['store_type'] = info_json["@type"]
            item['other_fields'] = ""
            item['coming_soon'] = "0"
            yield item

