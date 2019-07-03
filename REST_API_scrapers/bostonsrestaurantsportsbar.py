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

class bostonsrestaurantsportsbar(scrapy.Spider):
  name = 'bostonsrestaurantsportsbar'
  domain = ''
  history = []

  def start_requests(self):
    init_url = 'https://www.bostons.com/get-restaurant-locations'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    print("=========  Checking.......")
    store_list = json.loads(response.body)
    for store in store_list:
      item = ChainItem()
      item['store_name'] = self.validate(store['name'])
      item['address'] = self.validate(store['address'])
      item['city'] = self.validate(store['city'])
      item['state'] = self.validate(store['state_code'])
      item['zip_code'] = self.validate(store['zip'])
      item['country'] = 'United States'
      item['phone_number'] = self.validate(store['phone'])
      item['latitude'] = self.validate(str(store['coords']['lat']))
      item['longitude'] = self.validate(str(store['coords']['lng']))
      item['store_hours'] = 'Monday ' + self.validate(store['opening']['from-monday']) + '-' + self.validate(store['opening']['to-monday']) + ', '
      item['store_hours'] += 'Tuesday ' + self.validate(store['opening']['from-tuesday']) + '-' + self.validate(store['opening']['to-tuesday']) + ', '
      item['store_hours'] += 'Wednesday ' + self.validate(store['opening']['from-wednesday']) + '-' + self.validate(store['opening']['to-wednesday']) + ', '
      item['store_hours'] += 'Thursday ' + self.validate(store['opening']['from-thursday']) + '-' + self.validate(store['opening']['to-thursday']) + ', '
      item['store_hours'] += 'Friday ' + self.validate(store['opening']['from-friday']) + '-' + self.validate(store['opening']['to-friday']) + ', '
      item['store_hours'] += 'Saturday ' + self.validate(store['opening']['from-saturday']) + '-' + self.validate(store['opening']['to-saturday']) + ', '
      item['store_hours'] += 'Sunday ' + self.validate(store['opening']['from-sunday']) + '-' + self.validate(store['opening']['to-sunday'])
      yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''