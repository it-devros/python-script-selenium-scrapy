import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class DoublepizzaSpider(scrapy.Spider):
    name = 'doublepizza'
    domain = 'http://www.doublepizza.net'
    start_url = 'http://www.doublepizza.net/doublepizza/frontend.do?operation=goToStoreLocator'

    def start_requests(self):
        url = self.start_url
        yield scrapy.Request(url=url, callback=self.parse_stores)
    
    def parse_stores(self, response):
        stores_list = response.xpath('//div[@id="product_list"]//li')
        for store in stores_list:
            store_title = store.xpath('./table//tr//td//span[@class="store-title"]/text()').extract_first()
            store_addr = store.xpath('./table//tr//td//span[@class="address"]/text()').extract()
            addr = store_addr[0]
            city_state = store_addr[1].split(', ')
            city = city_state[0]
            state = city_state[1]
            
            hours = store.xpath('./table//tr//td//span[@class="store-hours"]/text()').extract()
            days = store.xpath('./table//tr//td//span[@class="daysOfWeek"]/text()').extract()
            i = 0
            store_hours = ''
            for day in days:
                store_hours += day + ':'
                store_hours += hours[i] + '; '
                i += 1
            print(store_hours)

            item = ChainItem()
            item['store_name'] = store_title
            item['address'] = addr
            item['city'] = city
            item['state'] = state
            item['country'] = 'Canada'
            item['store_hours'] = store_hours

            yield item