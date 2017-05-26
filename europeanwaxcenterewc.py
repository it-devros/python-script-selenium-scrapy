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

class europeanwaxcenterewc(scrapy.Spider):
    name = 'europeanwaxcenterewc'
    domain = 'http://www.waxcenter.com'
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        for location in self.location_list:
            init_url = 'http://www.waxcenter.com/locations-results?lat=%s&lng=%s&search=%s' % (str(location['latitude']), str(location['longitude']), location['city'].replace(' ', '-'))
            yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = response.xpath('//div[@class="search-center-details"]')
        if store_list:
            for store in store_list:
                url = self.validate(store.xpath('.//a[@class="lnk-a action search-results-detials center-info"]/@href').extract_first())
                url = self.domain + url
                request = scrapy.Request(url=url, callback=self.parse_detail)
                request.meta['store_name'] = self.validate(store.xpath('./h3[@class="search-results-name"]/a/text()').extract_first())
                request.meta['address'] = self.validate(store.xpath('.//span[@itemprop="streetAddress"]/text()').extract_first().replace('  ', '').replace(',', ''))
                request.meta['city'] = self.validate(store.xpath('.//span[@itemprop="addressLocality"]/text()').extract_first())
                request.meta['state'] = self.validate(store.xpath('.//span[@itemprop="addressRegion"]/text()').extract_first())
                request.meta['zip_code'] = self.validate(store.xpath('.//span[@itemprop="postalCode"]/text()').extract_first())
                request.meta['phone_number'] = self.validate(store.xpath('.//span[@itemprop="telephone"]/text()').extract_first())
                request.meta['latitude'] = self.validate(store.xpath('.//meta[@itemprop="latitude"]/@content').extract_first())
                request.meta['longitude'] = self.validate(store.xpath('.//meta[@itemprop="longitude"]/@content').extract_first())
                yield request

    def parse_detail(self, response):
        temp = self.validate(response.body.split("/api/center/hours?locationNumber=' + '")[1].split("',")[0])
        store_number = temp[2:]
        if not store_number in self.history:
            self.history.append(store_number)
            url = 'http://www.waxcenter.com/api/center/hours?locationNumber=' + temp
            header = {
                "Accept":"application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding":"gzip, deflate, br",
                "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With":"XMLHttpRequest"
            }
            request = scrapy.Request(url=url, headers=header, callback=self.parse_hour)
            request.meta['store_number'] = store_number
            request.meta['store_name'] = response.meta['store_name']
            request.meta['address'] = response.meta['address']
            request.meta['city'] = response.meta['city']
            request.meta['state'] = response.meta['state']
            request.meta['zip_code'] = response.meta['zip_code']
            request.meta['phone_number'] = response.meta['phone_number']
            request.meta['latitude'] = response.meta['latitude']
            request.meta['longitude'] = response.meta['longitude']
            yield request

    def parse_hour(self, response):
        item = ChainItem()
        item['store_hours'] = self.validate(response.body.replace('<br/>', ', ').replace('"', ''))
        item['store_number'] = response.meta['store_number']
        item['store_name'] = response.meta['store_name']
        if item['store_name'].find('Opening Soon') != -1:
            item['store_name'] = self.validate(item['store_name'].replace('Opening Soon', '').replace('-', ''))
            item['coming_soon'] = '1'
        item['address'] = response.meta['address']
        item['city'] = response.meta['city']
        item['state'] = response.meta['state']
        item['zip_code'] = response.meta['zip_code']
        item['phone_number'] = response.meta['phone_number']
        item['latitude'] = response.meta['latitude']
        item['longitude'] = response.meta['longitude']
        item['country'] = 'United States'
        yield item

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''