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

class americaneagleoutfitters(scrapy.Spider):
    name = 'americaneagleoutfitters'
    domain = 'https://www.ae.com'
    history = []

    def start_requests(self):
        init_url = 'http://storelocations.ae.com/locations.html'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = json.loads(response.body)
        for store in store_list['locations']:
            store = store['loc']
            if self.validate(store['country']) == 'United States':
                item = ChainItem()
                item['address'] = self.validate(store['address1'])
                item['address2'] = self.validate(store['address2'])
                item['city'] = self.validate(store['city'])
                item['country'] = self.validate(store['country'])
                item['store_number'] = self.validate(str(store['id']))
                item['latitude'] = self.validate(str(store['latitude']))
                item['longitude'] = self.validate(str(store['longitude']))
                item['store_name'] = self.validate(store['name']) + ' ' + self.validate(store['mallName'])
                item['phone_number'] = self.validate(store['phone'])
                item['zip_code'] = self.validate(store['postalCode'])
                item['state'] = self.validate(store['state'])
                temp_list = store['hours']['days']
                hours = ''
                if temp_list:
                    count = len(temp_list)
                    start_temp = ''
                    end_temp = ''
                    for temp in temp_list:
                        try:
                            start_temp = self.validate(str(temp['intervals'][0]['start']))
                            end_temp = self.validate(str(temp['intervals'][0]['end']))
                        except:
                            start_temp = ''
                            end_temp = ''
                        if start_temp and end_temp:
                            start = self.validate_(start_temp)
                            end = self.validate_(end_temp)
                            hours += temp['day'] + ': ' + start + '-' + end + ', '
                item['store_hours'] = self.validate(hours[:-2])
                yield item

    def validate_(self, item):
        length = len(item)
        st = ''
        if length == 4:
            st = item[:2] + ':' + item[2:]
        elif length == 3:
            st = item[:1] + ':' + item[1:]
        return st

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''