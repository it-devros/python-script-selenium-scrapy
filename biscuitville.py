import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class BiscuitvilleSpider(scrapy.Spider):
    name = 'biscuitville'
    domain = 'http://biscuitville.com/'
    request_url = 'http://biscuitville.com/locations'

    def start_requests(self):
        url = self.request_url
        yield scrapy.Request(url=url, callback=self.parse_stores)

    def parse_stores(self, response):
        if response.body:
            _response = response.body
            response_list = _response.split('"markers":[{')
            _response = response_list[1]
            response_list = _response.split('}],')
            _response = response_list[0].replace('\\u0022\\u003E', '').replace('\\u003C\\/', '')
            store_list = _response.split('},{')
            for store in store_list:
                item = ChainItem()
                store_li = store.split('"latitude":')
                store = store_li[1]
                temp_list = store.split(',')
                item['latitude'] = temp_list[0]
                store_li = store.split('"longitude":')
                store = store_li[1]
                temp_list = store.split(',')
                item['longitude'] = temp_list[0]
                store_li = store.split('"markername":"')
                store = store_li[1]
                temp_list = store.split('",')
                item['store_name'] = temp_list[0]
                store_li = store.split('streetAddress')
                store = store_li[1]
                temp_list = store.split('span')
                item['address'] = temp_list[0].strip()
                item['address'] = item['address'][:-1]
                store_li = store.split('postalCode')
                store = store_li[1]
                temp_list = store.split('span')
                item['zip_code'] = temp_list[0].strip()
                store_li = store.split('addressLocality')
                store = store_li[1]
                temp_list = store.split('span')
                item['city'] = temp_list[0].replace('\\n', '').strip()
                store_li = store.split('addressRegion')
                store = store_li[1]
                temp_list = store.split('span')
                item['state'] = temp_list[0].strip()
                store_li = store.split('Store #')
                store = store_li[1]
                temp_list = store.split('div')
                item['store_number'] = temp_list[0].strip()
                store_li = store.split('Phone:')
                store = store_li[1]
                temp_list = store.split('div')
                item['phone_number'] = temp_list[0].replace('a\\u003E', '').strip()
                store_li = store.split('Hours')
                store = store_li[1]
                temp_list = store.split('div')
                temp_hour = temp_list[0].replace('a\\u003Eem\\u003Ep\\u003E\\n\\n\\u003Cp\\u003E', '').replace('p\\u003E\\n', '').replace('\\u003Cbr \\/\\u003E\\n', '; ').replace('\u0026nbsp;', ' ').replace('\n\u003Cp\u003E', '').strip()
                if temp_hour.find('\u003E') != -1:
                    item['store_hours'] = temp_hour[:-15]
                else:
                    item['store_hours'] = temp_hour
                item['country'] = 'United States'
                yield item
        else:
            print('+++++++++++++++++++++++++ no response')
