import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class CitizensofhumSpider(scrapy.Spider):
    name = 'citizensofhum'
    domain = 'https://www.citizensofhumanity.com'
    request_url = 'https://www.citizensofhumanity.com/stores'

    def start_requests(self):
        url = self.request_url
        yield scrapy.Request(url=url, callback=self.body)

    def body(self, response):
        print("=========  Checking.......")
        _response = response.body
        if _response:
            stores_list = _response.split('initial_locations:  [{')
            stores_str = stores_list[1]
            stores_list = stores_str.split('],')
            stores_str = stores_list[0]
            store_list = stores_str.split('},{')
            for store in store_list:
                item = ChainItem()
                store_li = store.split('"location_id":"')
                store = store_li[1]
                temp_list = store.split('",')
                item['store_number'] = temp_list[0]
                store_li = store.split('"title":"')
                store = store_li[1]
                temp_list = store.split('",')
                item['store_name'] = temp_list[0]
                store_li = store.split('"address":"')
                store = store_li[1]
                temp_list = store.split('",')
                temp_address = temp_list[0]
                
                temp_list = temp_address.split(', ')
                i = 0
                for li in temp_list:
                    i += 1
                j = 0
                address = ''
                while j < i - 2:
                    address += temp_list[j] + ' '
                    j += 1
                city = temp_list[i - 2]
                sz_list = temp_list[i - 1].split(' ')
                state = sz_list[0]
                zip_code = sz_list[1]
                
                item['address'] = address
                item['city'] = city
                item['state'] = state
                item['zip_code'] = zip_code

                store_li = store.split('"latitude":"')
                store = store_li[1]
                temp_list = store.split('",')
                item['latitude'] = temp_list[0]
                store_li = store.split('longitude')
                store = store_li[1]
                temp_list = store.split('",')
                item['longitude'] = temp_list[0].replace('":"', '')
                store_li = store.split('"phone":"')
                store = store_li[1]
                temp_list = store.split('",')
                item['phone_number'] = temp_list[0]
                store_li = store.split('"country":"')
                store = store_li[1]
                temp_list = store.split('",')
                if temp_list[0] == 'US':
                    item['country'] = 'United States'
                else:
                    item['country'] = temp_list[0]
                item['coming_soon'] = '0'
                yield item
                
        else:
            print('========================== response is not')

