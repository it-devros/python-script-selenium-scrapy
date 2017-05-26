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

class caseys(scrapy.Spider):
    name = 'caseys'
    domain = 'https://www.caseys.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.caseys.com/locations/list'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['address'] = self.validate(store['address'])
                item['city'] = self.validate(store['city'])
                if store['hours'] != 'Coming Soon':
                    item['store_hours'] = self.validate(store['hours'])
                else:
                    item['coming_soon'] = '1'
                item['latitude'] = self.validate(str(store['lat']))
                item['longitude'] = self.validate(str(store['lon']))
                item['phone_number'] = self.validate(store['phone'])
                item['state'] = self.validate(store['state'])
                item['store_number'] = self.validate(str(store['storeNumber']))
                item['store_name'] = self.validate(store['title'])
                item['zip_code'] = self.validate(str(store['zipcode']))
                item['country'] = 'United States'
                yield item
        else:
            pass

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''