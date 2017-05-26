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

class regalnailssalon_spa(scrapy.Spider):
    name = 'regalnailssalon_spa'
    domain = 'http://www.regalnails.com/'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_States.json'
        with open(file_path) as data_file:    
            self.US_States_list = json.load(data_file)

    def start_requests(self): 
        init_url = 'http://secure3.net-shapers.com/regalnailslocator/locator.php?zip=20010&distance=6000&locator_search_submit_range=Search'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//table[@class="location_search_results"]//tbody//tr')
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['store_name'] = self.validate(store.xpath('.//span[@class="location_name"]/text()').extract_first())
                item['phone_number'] = self.validate(store.xpath('.//span[@class="location_phone"]/text()').extract_first())
                address = store.xpath('.//span[@class="location_address"]/text()').extract()
                item['address'] = self.validate(address[0])
                addr = address[1]
                item['city'] = self.validate(addr.split(',')[0].replace('(n)', ''))
                item['state'] = self.validate(self.validate(addr.split(',')[1]).split(' ')[0])
                item['zip_code'] = self.validate(self.validate(addr.split(',')[1]).split(' ')[1])
                item['country'] = self.check_country(item['state'])
                yield item
        else:
            pass	

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