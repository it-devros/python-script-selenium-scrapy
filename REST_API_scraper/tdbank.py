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

class tdbank(scrapy.Spider):
    name = 'tdbank'
    domain = 'https://www.tdbank.com/'
    history = []

    def start_requests(self):
        init_url = 'https://www.tdbank.com/net/get11.ashx?longitude=-79.4692&latitude=43.739&searchradius=5000&searchunit=mi&locationtypes=3&numresults=3000&time=21:09&Json=y&callback='
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list['markers']['marker']:
                if store['coun'] == 'ca':
                    item = ChainItem()
                    item['country'] = 'Canada'
                    item['latitude'] = self.validate(store['lat'])
                    item['longitude'] = self.validate(store['lng'])
                    item['store_number'] = self.validate(store['id'])
                    item['phone_number'] = self.validate(store['phoneNo'])
                    hours = ''
                    count = len(store['hours'])
                    i = 0
                    for hour in store['hours']:
                        if hour != 'OpenNow':
                            if i < count - 2:
                                hours += hour + ' ' + store['hours'][hour] + ','
                            else:
                                hours += hour + ' ' + store['hours'][hour]
                            i += 1
                    item['store_hours'] = self.validate(hours)
                    addr = store['address']
                    addr_list = addr.split(',')
                    item['address'] = self.validate(addr_list[0])
                    item['city'] = self.validate(addr_list[1])
                    item['state'] = self.validate(addr_list[2])
                    item['zip_code'] = self.validate(addr_list[3])
                    yield item
                else:
                    pass
        else:
            pass

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''