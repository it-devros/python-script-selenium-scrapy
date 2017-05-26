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

class citizensbank(scrapy.Spider):
    name = 'citizensbank'
    domain = 'https://www.citizensbank.com'
    location_list = []
    history = []

    def __init__(self):
        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            self.location_list = json.load(data_file)

    def start_requests(self):
        init_url = 'https://www.citizensbank.com/apps/ApiProxy/BranchlocatorApi/api/BranchLocator'
        header = {
            "Accept":"application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding":"gzip, deflate, br",
            "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With":"XMLHttpRequest"
        }
        for location in self.location_list:
            frmdata = {
                'RequestHeader[RqStartTime]': '2017-05-16T00:09:25.354Z',
                'coordinates[Latitude]': str(location['latitude']),
                'coordinates[Longitude]': str(location['longitude']),
                'searchFilter[IncludeAtms]': 'false',
                'searchFilter[IncludeBranches]': 'false',
                'searchFilter[IncludeVoiceAssistedAtms]': 'false',
                'searchFilter[IncludeSuperMarketBranches]': 'false',
                'searchFilter[IncludeOpenNow]': 'false'
            }
            yield FormRequest(url=init_url, headers=header, callback=self.body, formdata=frmdata) 

    def body(self, response):
        store_list = json.loads(response.body)
        if store_list:
            for store in store_list['BranchCollection']:
                store_number = self.validate(store['BranchId'])
                if not store_number in self.history:
                    self.history.append(store_number)
                    item = ChainItem()
                    item['address'] = self.validate(store['Address']['StreetAddress']['Value'])
                    item['city'] = self.validate(store['Address']['City'])
                    item['latitude'] = self.validate(str(store['Address']['Coordinates']['Latitude']))
                    item['longitude'] = self.validate(str(store['Address']['Coordinates']['Longitude']))
                    item['country'] = 'United States'
                    item['state'] = self.validate(store['Address']['State'])
                    if store['Address']['Phone'] != 'NA':
                        item['phone_number'] = self.validate(store['Address']['Phone'])
                    item['zip_code'] = self.validate(store['Address']['Zip'])
                    item['store_name'] = self.validate(store['BranchName']['Value'])
                    item['store_hours'] = self.validate(store['LobbyHours']['Description'])
                    item['store_number'] = self.validate(store['BranchId'])
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
