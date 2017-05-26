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

class h2owireless(scrapy.Spider):
    name = 'h2owireless'
    domain = 'https://www.h2owirelessnow.com'
    history = []
    location_list = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/geocode.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        init_url = 'https://www.h2owirelessnow.com/mainControl.php?page=stores'
        for location in self.location_list:
            lat = self.validate(str(location['latitude']))
            lng = self.validate(str(location['longitude']))
            frmdata = {
                'step':'getStoresByZip',
                'zip':'',
                'lat':lat,
                'lng':lng
            }
            yield FormRequest(url=init_url, callback=self.body, formdata=frmdata) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list:
                store_id = store['id']
                if not store_id in self.history:
                    self.history.append(store_id)
                    item = ChainItem()
                    item['address'] = self.validate(store['address'].replace('&Amp;', ' ').replace('&amp;', ' '))
                    item['city'] = self.validate(store['city'])
                    item['store_number'] = self.validate(store['id'])
                    item['latitude'] = self.validate(store['lat'])
                    item['longitude'] = self.validate(store['lng'])
                    item['phone_number'] = self.validate(store['phone'])
                    item['state'] = self.validate(store['state'])
                    item['store_name'] = self.validate(store['store_name'].replace('&Amp;', ' ').replace('&amp;', ' '))
                    item['zip_code'] = self.validate(store['zip'])
                    item['country'] = 'United States'
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

    def validateZip(self, item):
        ziplength = len(item)
        if ziplength < 5:
            count = 5 - ziplength
            i = 0
            temp = ''
            while i < count:
                temp += '0'
                i += 1
            item = temp + item
        return item
