#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class orschelnfarmhome(scrapy.Spider):
    name = 'orschelnfarmhome'
    domain = 'https://www.orschelnfarmhome.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.orschelnfarmhome.com/view/page/stores'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        data = response.body.split('data.mixin({},')[1].split(');};;')[0].strip()
        valid_data = self.validate(data)
        store_list = json.loads(data)
        for store in store_list:
            item = ChainItem()
            item['store_number'] = store
            item['phone_number'] = store_list[store]['phone']
            item['store_hours'] = store_list[store]['hours']
            item['zip_code'] = store_list[store]['zipcode']
            item['state'] = store_list[store]['state']
            item['country'] = store_list[store]['country']
            item['city'] = store_list[store]['city']
            item['store_name'] = store_list[store]['sku_name']
            item['address'] = store_list[store]['address']
            item['latitude'] = store_list[store]['latitude']
            item['longitude'] = store_list[store]['longitude']
            yield item

    def validate(self, item):
        try:
            return item.encode('raw-unicode-escape').strip()
        except:
            return ''


