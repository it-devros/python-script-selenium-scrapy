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

class thriftywhite(scrapy.Spider):
    name = 'thriftywhite'
    domain = 'http://www.thriftywhite.com'
    history = []

    def start_requests(self):
        init_url = 'http://www.thriftywhite.com/store_locations_new.cfm?CFID=2050737&CFTOKEN=6053348e432d0111-1FCF2F8E-A3FF-58B1-E513F22F2D85B2A8&jsessionid=f0308c9aab60af86bb884b37706a244d1255'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        res = self.getValue(response.body, 'add the points', '// put the assembled side_bar_html')
        if res:
            store_list = res.split('var point')
            for store in store_list:
                store = self.validate(store)
                if store:
                    item = ChainItem()
                    item['latitude'] = self.getValue(store, 'LatLng(', ',')
                    item['longitude'] = self.getValue(store, ',', ');')
                    item['store_name'] = self.getValue(store, '(point,"', '","')
                    item['city'] = self.getElement(store, 1)
                    item['state'] = self.getElement(store, 2)
                    item['zip_code'] = self.getElement(store, 3)
                    item['store_number'] = self.getElement(store, 6)
                    item['address'] = self.getValue(store, '</cfif><tr><td>', '</td>')
                    if item['address'] == '' or len(item['address']) < 10:
                        item['address'] = self.getValue(store, '<tr><td>', '</td>')
                    item['phone_number'] = self.getValue(store, '<td>Phone:', '</td>')
                    html_string = self.getElement(store, 4)
                    info = etree.HTML(html_string)
                    hour_info = info.xpath('//table[@class="mapText"]//tr')[0]
                    hours = ''
                    if hour_info:
                        try:
                            str_hour = hour_info.xpath('//td/text()')
                            temp_hour = []
                            i = 0
                            for hour in str_hour:
                                if i > 3:
                                    if not hour.strip() in temp_hour:
                                        temp_hour.append(hour.strip())
                                        hours += hour.strip() + ' '
                                i += 1
                        except:
                            hours = ''
                    item['store_hours'] = hours
                    item['country'] = 'United States'
                    yield item
                else:
                    pass
        else:
            pass

    def getValue(self, item, str1, str2):
        try:
            return item.split(str1)[1].split(str2)[0].strip()
        except:
            return ''

    def getElement(self, item, index):
        try:
            return item.split('","')[index].strip()
        except:
            return ''

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''