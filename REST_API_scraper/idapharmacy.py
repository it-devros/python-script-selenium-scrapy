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
import pdb

class idapharmacy(scrapy.Spider):
  name = 'idapharmacy'
  domain = ''
  history = []

  def start_requests(self):
    
    init_url = 'https://www.ida-pharmacy.ca/store-locator-ws/stores/search/1?swLatitude=5.98412454474825&swLongitude=-160.3546129648438&neLatitude=68.01448716131918&neLongitude=-49.085081714843795'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    print("=========  Checking.......")
    store_list = json.loads(response.body)
    for store in store_list:
      item = ChainItem()
      item['store_name'] = store['name']
      item['store_number'] = store['id']
      item['address'] = store['address']
      item['city'] = store['city']
      item['state'] = store['provinceCode']
      item['zip_code'] = store['postalCode']
      item['country'] = 'Canada'
      item['phone_number'] = store['phone']
      item['latitude'] = store['latitude']
      item['longitude'] = store['longitude']
      item['store_hours'] = store['hours']
      item['store_type'] = ''
      item['other_fields'] = ''
      item['coming_soon'] = ''
      if item['store_number'] not in self.history:
        self.history.append(item['store_number'])
        yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''