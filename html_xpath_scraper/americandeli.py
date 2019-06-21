import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class AmericandeliSpider(scrapy.Spider):
    name = 'americandeli'
    domain = 'http://www.americandeli.com/'
    start_url = 'http://www.americandeli.com/frames/location_list'
    request_urls = []

    def start_requests(self):
        url = self.start_url
        yield scrapy.Request(url=url, callback=self.parse_stores)

    def parse_stores(self, response):
        stores_link_eles = response.xpath('//div[@id="main"]//div[@class="contentac"]//div//ul//li//a')
        if stores_link_eles:
            for stores_link_ele in stores_link_eles:
                store_link = stores_link_ele.xpath('./@href').extract_first()
                self.request_urls.append(store_link)
            for request_url in self.request_urls:
                yield scrapy.Request(url=request_url, callback=self.parse_detail)
            # yield scrapy.Request(url='http://www.americandeli.com/stores/page/savannah', callback=self.parse_detail)
        else:
            print('there are no stores.')

    def parse_detail(self, response):
        shop_name = response.xpath('//h2[@class="h2top"]/text()').extract_first()
        if shop_name:
            store__list_eles = response.xpath('//div[@class="addresses"]//ul//li[@class="moreLandaddress"]')

            store_addr_list = store__list_eles[0].xpath('.//p/text()').extract()
            store_addr_list[0] = store_addr_list[0].replace('\n', ' ')
            addr = store_addr_list[0]
            city_state_zip = store_addr_list[1].split(', ')
            city = city_state_zip[0]
            state = city_state_zip[1]
            zip_code = city_state_zip[2]

            hour = ''
            store_hour_list = store__list_eles[1].xpath('.//p/text()').extract()
            if store_hour_list:
                for store_hour in store_hour_list:
                    temp_hour = store_hour.strip().encode('raw-unicode-escape').replace('\u2013', ' - ')
                    hour += temp_hour + '; '

            item = ChainItem()
            item['store_name'] = shop_name
            item['address'] = addr
            item['city'] = city
            item['state'] = state
            item['zip_code'] = zip_code
            item['store_hours'] = hour
            item['country'] = 'United States'

            yield item
        else:
            print('++++++++++++++++++++++++++++++++++++++++++ deleted')
            

