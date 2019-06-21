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
import unicodedata

class hobbylobbystores(scrapy.Spider):
    name = 'hobbylobbystores'
    domain = 'https://www.hobbylobby.com'
    location_list = []
    history1 = []
    history2 = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/US_Cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        for location in self.location_list:
            city = location['city']
            init_url = 'https://www.hobbylobby.com/store-finder?q=' + self.validate(city.replace(' ', '+'))
            yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//div[@class="store-result clearfix"]')
        for store in store_list:
            link = self.validate(store.xpath('./div[@class="store-result-block"]//a[@class="button tertiary utility"]/@href').extract_first())
            if link:
                detail_url = self.domain + link
                yield scrapy.Request(url=detail_url, callback=self.parse_detail)
            else:
                temp_list = store.xpath('./div[@class="store-result-block"]')[1].xpath('.//ul//li')
                try:
                    address = self.validate(temp_list[0].xpath('./text()').extract_first())
                    if not address in self.history2:
                        self.history2.append(address)
                        item = ChainItem()
                        temp = ''
                        try:
                            item['address'] = self.validate(temp_list[0].xpath('./text()').extract_first())
                            temp = self.validate(temp_list[1].xpath('./text()').extract_first())
                        except:
                            pass
                        try:
                            temp_list = temp.split(',')
                            item['city'] = self.validate(temp_list[0])
                            item['state'] = self.validate(self.format(temp_list[1].strip()).split(' ')[0])
                            temp_list = self.validate(self.format(temp_list[1].strip())).split(' ')
                            count = len(temp_list)
                            item['zip_code'] = self.validate(temp_list[count - 1])
                        except:
                            pass
                        item['coming_soon'] = '1'
                        item['country'] = 'United States'
                        yield item
                except:
                    pass

    def parse_detail(self, response):
        temp = self.validate(response.xpath('//div[@class="store_map_details"]/@data-stores').extract_first())
        try:
            store_list = json.loads(temp)
            store = store_list[0]
            temp = self.validate(store['name'])
            store_number = self.validate(temp.split('#')[1])
            try:
                if not store_number in self.history1:
                    self.history1.append(store_number)
                    item = ChainItem()
                    item['latitude'] = self.validate(store['latitude'])
                    item['longitude'] = self.validate(store['longitude'])
                    item['store_name'] = self.validate(temp.split('#')[0])
                    item['store_number'] = self.validate(temp.split('#')[1])
                    item['address'] = self.validate(store['address1'])
                    item['address2'] = self.validate(store['address2'])
                    item['city'] = self.validate(store['city'])
                    item['state'] = self.validate(store['stateProvince'])
                    item['zip_code'] = self.validate(store['zipcode'])
                    item['country'] = self.validate(store['country'])
                    hours = ''
                    temp_list = response.xpath('//table[@class="store-openings weekday_openings"]//tbody//tr')
                    if temp_list:
                        for temp in temp_list:
                            hours += self.validate(temp.xpath('./td[@class="weekday_openings_day"]/text()').extract_first()) + self.validate(temp.xpath('./td[@class="weekday_openings_times"]/text()').extract_first()) + ', '
                    item['store_hours'] = self.validate(hours[:-2])
                    temp_list = response.xpath('//ul[@class="address"]//li')
                    item['phone_number'] = self.validate(temp_list[2].xpath('./text()').extract_first())
                    yield item
            except:
                pass
        except:
            pass

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''

    def format(self, item):
        try:
            return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
        except:
            return ''