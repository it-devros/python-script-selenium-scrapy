import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html

class hottopic(scrapy.Spider):
    name = 'hottopic'
    domain = 'http://www.hottopic.com/'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_States.json'
        with open(file_path) as data_file:    
            self.US_States_list = json.load(data_file)

    def start_requests(self): 
        init_url = 'http://www.hottopic.com/on/demandware.store/Sites-hottopic-Site/default/Responsive-LoadDynamicContentSlot?slotid=cat-landing-banner-top&catid=cs-allstores'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//div[@class="html-slot-container"]//div//div')
        if store_list:
            for store in store_list:
                temp = store.xpath('./a/@href').extract_first()
                temp = self.validate(temp)
                request = scrapy.Request(url=temp, callback=self.parse_detail)
                request.meta['store_number'] = self.validate(temp.split('StoreID=')[1])
                temp_list = store.xpath('./ul//li')
                temp1_list = temp_list[0].xpath('./text()').extract()
                request.meta['address'] = self.validate(temp1_list[0].split(',')[0])
                request.meta['address2'] = self.validate(temp1_list[0].split(',')[1])
                request.meta['city'] = self.validate(temp1_list[1].strip().split(',')[0])
                request.meta['state'] = self.validate(temp1_list[1].strip().split(',')[1].strip().split(' ')[0])
                request.meta['zipcode'] = self.validate(temp1_list[1].replace('#', '').strip().split(',')[1].strip().split(' ')[1])
                request.meta['phone'] = self.validate(temp_list[1].xpath('./text()').extract_first().replace('Phone:', '').replace('.', '-'))
                yield request

    def parse_detail(self, response):
        temp_list = response.xpath('//div[@class="about-store"]')
        if temp_list:
            try:
                item = ChainItem()
                item['store_number'] = response.meta['store_number']
                item['store_name'] = self.validate(temp_list.xpath('./h1/text()').extract_first())
                temp_list = temp_list.xpath('.//p')
                item['address'] = self.validate(temp_list[1].xpath('./text()').extract_first())
                item['address2'] = self.validate(temp_list[2].xpath('./text()').extract_first())
                temp = self.validate(temp_list[3].xpath('./text()').extract_first())
                item['city'] = self.validate(temp.split(',')[0])
                item['state'] = self.validate(temp.split(',')[1])
                item['zip_code'] = self.validate(temp.split(',')[2])
                item['country'] = self.check_country(item['state'])
                item['phone_number'] = self.validate(response.xpath('//p[@class="phone-number"]/text()').extract_first().replace('.', '-'))
                item['store_hours'] = self.validate(response.xpath('//span[@class="store-hours"]/text()').extract_first())
                yield item
            except:
                item = ChainItem()
                item['store_number'] = response.meta['store_number']
                item['address'] = response.meta['address']
                item['address2'] = response.meta['address2']
                item['city'] = response.meta['city']
                item['state'] = response.meta['state']
                item['zip_code'] = response.meta['zipcode']
                item['phone_number'] = response.meta['phone']
                item['country'] = self.check_country(item['state'])
                yield item

    def check_country(self, item):
        if 'PR' in item:
            return 'Puert Rico'
        else:
            for state in self.US_States_list:
                if item in state['abbreviation']:
                    return 'United States'
            return 'Canada'

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''