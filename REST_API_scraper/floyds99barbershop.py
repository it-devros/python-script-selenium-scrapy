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

class floyds99barbershop(scrapy.Spider):
    name = 'floyds99barbershop'
    domain = 'https://www.floydsbarbershop.com'
    history = []

    def start_requests(self):
        init_url = 'https://www.floydsbarbershop.com/modules/staff/ajax.aspx'
        frmdata = {
            'StartIndex': '0',
            'EndIndex': '10000',
            'Longitude': '42.0027',
            'Latitude': '-87.90084',
            'StateCode': '',
            'RangeInMiles':'5000',
            'F': 'GetNearestLocations'
        }
        yield FormRequest(url=init_url, callback=self.body, formdata=frmdata) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list:
                item = ChainItem()
                item['address'] = self.validateAddr(store['Address1'])
                item['address2'] = store['Address2']
                item['city'] = store['City']
                if store['IsComingSoon'] == 'true':
                    item['coming_soon'] = '1'
                item['latitude'] = store['Latitude']
                item['longitude'] = store['Longitude']
                item['store_name'] = store['Name']
                hours = self.getHours(store['OpenHours'])
                item['store_hours'] = hours
                item['phone_number'] = store['Phone']
                item['state'] = store['State']
                item['zip_code'] = store['Zip']
                item['country'] = 'United States'
                yield item
        else:
            pass
    
    def validateAddr(self, item):
            try:
                return item.replace(',', '').strip()
            except:
                return item

    def getHours(self, _list):
        hours = ''
        count = len(_list)
        i = 0
        for day in _list:
            if i < count - 1:
                hours += day['DayName'] + ': ' + day['OpenHrs'] + ' - ' + day['CloseHrs'] + ', '
            else:
                hours += day['DayName'] + ': ' + day['OpenHrs'] + ' - ' + day['CloseHrs']
            i += 1
        return hours

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''