import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

import zipcode
from pypostalcode import PostalCodeDatabase

class DiorSpider(scrapy.Spider):
    name = "dior"
    stores_per_page = 21

    domain = "http://en.store.dior.com"
    start_urls = ["http://en.store.dior.com/search?st_any%5BCATEGORIES%5D%5B%5D=Fashion+%26+Accessories&country=ca&query=&st_join=and", "http://en.store.dior.com/search?st_any%5BCATEGORIES%5D%5B%5D=Fragrance+%26+Beauty&country=ca&query=&st_join=and", "http://en.store.dior.com/search?st_any%5BCATEGORIES%5D%5B%5D=Fashion+%26+Accessories&country=us&query=&st_join=and", "http://en.store.dior.com/search?st_any%5BCATEGORIES%5D%5B%5D=Fragrance+%26+Beauty&country=us&query=&st_join=and"]

    def __init__(self):
        self.pcdb = PostalCodeDatabase()
    
    # calculate number of pages
    def parse(self, response):
        # get total number of stores
        total = int(response.xpath("//span[@class='pos-results-amount']/text()").extract_first().strip().split(" ")[0])
        pages = int(total / self.stores_per_page) + (total % self.stores_per_page > 0)

        # make a request for scraping data from the 1st page
        page = 1
        url = "%s&page=%d" % (response.url, page)
        request = scrapy.Request(url=url, callback=self.parse_page)
        request.meta["url"] = response.url
        request.meta["page"] = page
        request.meta["total_pages"] = pages

        yield request

    # crawl data from each page
    def parse_page(self, response):
        origin_url = response.meta["url"]
        page = response.meta["page"]
        total_pages = response.meta["total_pages"]

        stores = response.xpath("//div[@class='pos-results-pos-info-container']")
        for store in stores:
            url = self.domain + store.xpath(".//h4[@class='pos-results-pos-name']//a/@href").extract_first().strip()
            request = scrapy.Request(url=url, callback=self.parse_store)
 
            if response.url.find("country=us") != -1:
                request.meta["country"] = "United States"
            else:
                request.meta["country"] = "Canada"
            yield request

        page += 1

        # check if the current page is the end or not
        if page > total_pages:
            return

        # make a request for scraping data from the next page
        url = "%s&page=%d" % (origin_url, page)
        request = scrapy.Request(url=url, callback=self.parse_page)
        request.meta["url"] = origin_url
        request.meta["page"] = page
        request.meta["total_pages"] = total_pages
        yield request

    # pare store detail page
    def parse_store(self, response):
        item = ChainItem()
	item['store_name'] = self.validate(response.xpath("//h1[@class='pos-detail-store-name']/text()"))
	item['store_number'] = ''
	item['phone_number'] = self.validate(response.xpath("//p[@class='pos-detail-phone-number']/text()"))[4:].strip()
	item['city'] = self.validate(response.xpath("//span[@class='pos-city']/text()"))
	item['country'] = response.meta["country"]
	item['state'] = ""
	item['zip_code'] = self.validate(response.xpath("//span[@class='pos-postal-code']/text()"))
        temp = item['zip_code'].split(" ")

        if item['country'] == "United States" and len(temp) > 1:
            if len(temp[0]) == 2:
                item['state'] = temp[0]
                item['zip_code'] = temp[1]
            else:
                item['state'] = temp[1]
                item['zip_code'] = temp[0]
        if item['country'] == "Canada" and len(temp) > 2:
            tp_zip, tp_state = [], ""
            for tp in temp:
                if len(tp) == 2:
                    tp_state = tp
                else:
                    tp_zip.append(tp)
            item['state'] = tp_state
            item['zip_code'] = " ".join(tp_zip)

        if item['zip_code'].strip() != "":
            try:
                if item['country'] == "Canada":
                    item["state"] = self.pcdb[str(item['zip_code'].split(" ")[0])].province
                else:
                    item["state"] = zipcode.isequal(str(item['zip_code'])).state
            except:
                pass

	item['latitude'] = ''
	item['longitude'] = ''

        address = self.validate(response.xpath("//address[@class='pos-detail-store-address']/text()"))
	item['address'] = address.replace("\n", "").strip()
        
        open_hrs = response.xpath("//ul[@class='opening-hours']//li")
        open_hrs_list = []
        if len(open_hrs) > 0:
            for hr in open_hrs:
                open_hrs_list.append(self.validate(hr.xpath(".//meta/@content")))

	item['store_hours'] = "; ".join(open_hrs_list)
	#item['store_type'] = info_json["@type"]
	item['other_fields'] = ''
	item['coming_soon'] = '0'

        yield item

    def validate(self, xpath_obj):
        try:
            return xpath_obj.extract_first().strip()
        except:
            return ""

