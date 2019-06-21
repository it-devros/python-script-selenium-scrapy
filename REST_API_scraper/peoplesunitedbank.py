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

class peoplesunitedbank(scrapy.Spider):
    name = 'peoplesunitedbank'
    domain = 'https://www.peoples.com'
    history = []

    def start_requests(self):    
        init_url = 'https://www.mapquestapi.com/search/v2/radius?key=Gmjtd%7Cluu22hu1n9%2C80%3Do5-lzal9&callback=renderBasicSearchNarrative&inFormat=json&json={origin:%27New%20York,%20New%20York%20County,%20NY%20US%27,hostedDataList:[{%27tableName%27:%27mqap.37221_PUB_BRANCHES%27,%27extraCriteria%27:%27%27,%27fields%27:[ATMmachine,Safe,OfficeNumber,postal,Hours,state,N,NightDeposit,country,city,T,county,address,DriveThruHour,lat,lng,traditionalBranch,stopshopBranch,DriveUp,ATM,NightDepositAvail,DriveUpATM,SafeDeposit,SelfCoinMach,Status,weburl]}],options:{%27shapeFormat%27:%27cmp6%27,%27radius%27:%273000%27,%27currentPage%27:%271%27,%27maxMatches%27:%271000%27,%27units%27:%27m%27}}'
        yield scrapy.Request(url=init_url, callback=self.body) 

    def body(self, response):
        str_stores = response.body.replace('renderBasicSearchNarrative(', '').replace(');', '').strip()
        store_list = json.loads(str_stores)
        if store_list:
            for store in store_list['searchResults']:
                item = ChainItem()
                item['store_name'] = self.validate(store['name'])
                item['store_hours'] = self.validate(store['fields']['Hours'])
                item['latitude'] = self.validate(str(store['fields']['mqap_geography']['latLng']['lat']))
                item['longitude'] = self.validate(str(store['fields']['mqap_geography']['latLng']['lng']))
                item['phone_number'] = self.validate(store['fields']['OfficeNumber'])
                item['address'] = self.validate(store['fields']['address'])
                item['city'] = self.validate(store['fields']['city'])
                item['state'] = self.validate(store['fields']['state'])
                item['zip_code'] = self.validate(store['fields']['postal'])
                if store['fields']['country'] == 'US':
                    item['country'] = 'United States'
                else:
                    item['country'] = self.validate(store['fields']['country'])
                yield item
        else:
            pass		

    def validate(self, item):
        try:
            return item.strip()
        except:
            return ''