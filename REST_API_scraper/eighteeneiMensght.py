import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
import unicodedata
from lxml import html

class eighteeneiMensght(scrapy.Spider):
    name = 'eighteeneiMensght'
    domain = 'http://eighteeneight.com'
    history = []

    def start_requests(self):
        init_url = 'http://eighteeneight.com/wp-admin/admin-ajax.php?action=store_search&lat=38.9339046&lng=-77.03053899999998&max_results=500&radius=5000'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['address'] = self.format(store['address']).replace(',', '')
                item['address2'] = self.format(store['address2'])
                item['city'] = self.format(store['city']).replace('NJ', '').replace(',', '')
                item['country'] = self.format(store['country'])
                item['store_number'] = store['id']
                item['latitude'] = store['lat']
                item['longitude'] = store['lng']
                item['phone_number'] = store['phone']
                item['state'] = self.format(store['state'])
                store_name = self.format(store['store'])
                item['store_name'] = self.validateStoreName(store_name)[1]
                item['coming_soon'] = self.validateStoreName(store_name)[0]
                item['zip_code'] = store['zip']
                hours = store['hours']
                item['store_hours'] = self.validateHours(hours)
                yield item
        else:
            pass			

    def validateHours(self, item):
        try:
            s_hour = etree.HTML(item)
            hours = s_hour.xpath('//p/text()')
            return self.getHours(hours)
        except:
            return ''

    def getHours(self, _list):
        if _list:
            value = ''
            count = len(_list)
            i = 0
            for hour in _list:
                hour = hour.encode('raw-unicode-escape')
                if i < count - 1 and hour:
                    value += hour.replace('\u2013', '').replace('\u00a0', '').strip() + ', '
                else:
                    value += hour.replace('\u2013', '').replace('\u00a0', '').strip()
                i += 1
            return value
        else:
            return ''

    def validateStoreName(self, item):
        value = ['', '']
        if item.find('COMING SOON') != -1:
            value[0] = '1'
            value[1] = item.replace('; COMING SOON', '').replace('&#8211', '').replace(';', '')
        elif item.find('Coming Soon') != -1:
            value[0] = '1'
            value[1] = item.replace('; Coming Soon', '').replace('&#8211', '').replace(';', '')
        elif item.find('NOW OPEN') != -1:
            value[1] = item.replace('; NOW OPEN', '').replace('&#8211', '').replace(';', '')
        elif item.find('Now Open') != -1:
            value[1] = item.replace('; Now Open', '').replace('&#8211', '').replace(';', '')
        else:
            value[1] = item.replace('&#8211', '').replace(';', '')
        value[1] = value[1].replace('!', '').strip()
        return value

    def format(self, item):
        try:
            return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
        except:
            return ''