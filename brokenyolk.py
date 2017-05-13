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

class brokenyolk(scrapy.Spider):
    name = 'brokenyolk'
    domain = 'http://thebrokenyolkcafe.com'
    history = []
    stores = []

    def start_requests(self):
        init_url = 'http://thebrokenyolkcafe.com/wp-content/themes/RML-brokenyolk-corp/js/main.js'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        str_stores = self.getJsonString(response.body)
        if str_stores:
            self.stores = json.loads(str_stores)
            request_url = 'http://thebrokenyolkcafe.com/locations/'
            yield scrapy.Request(url=request_url, callback=self.parse_store)
        else:
            pass
    
    def parse_store(self, response):
        if self.stores:
            for store in self.stores:
                store_id = store['cid']
                phone_number = response.xpath('//a[@class="phone hidden"][@data-placeid="' + store_id + '"]/text()').extract_first()
                if not phone_number:
                    phone_number = response.xpath('//a[@class="phone"][@data-placeid="' + store_id + '"]/text()').extract_first()
                store_hours = response.xpath('//div[@class="hours hidden"][@data-placeid="' + store_id + '"]/text()').extract()
                if not store_hours:
                    store_hours = response.xpath('//div[@class="hours"][@data-placeid="' + store_id + '"]/text()').extract()
                item = ChainItem()
                item['store_name'] = store['title']
                item['latitude'] = store['lat']
                item['longitude'] = store['lng']
                item['store_number'] = store['cid']
                item['address'] = store['street']
                item['city'] = store['city']
                item['state'] = store['state']
                item['zip_code'] = store['zip']
                item['phone_number'] = self.validatePhone(phone_number)
                item['country'] = 'United States'
                item['store_hours'] = self.validateHours(store_hours)
                yield item
        else:
            pass
    
    def validatePhone(self, item):
        try:
            return item.replace('YOLK', '').replace('  ', ' ').replace(' ', '-').strip()
        except:
            return ''

    def validateHours(self, _list):
        try:
            if _list:
                hours = ''
                for hour in _list:
                    hours += self.validate(hour) + ' '
                return hours
            else:
                return ''
        except:
            return ''

    def getJsonString(self, item):
        try:
            return self.validate(item.split('allMarkers =')[1].split(';')[0])
        except:
            return ''

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''