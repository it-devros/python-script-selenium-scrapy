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

class blackangussteakhouse(scrapy.Spider):
  name = 'blackangussteakhouse'
  domain = 'https://www.blackangus.com/'
  history = []

  def start_requests(self):
    
    init_url = 'https://momentfeed-prod.apigee.net/api/llp.json?auth_token=YFNPECMVZGRQCXJC&pageSize=100'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):

    store_list = json.loads(response.body)
    print("=========  Checking.......", len(store_list))
    for store in store_list:
      item = ChainItem()
      item['store_name'] = self.validate(store['store_info']['name'])
      item['store_number'] = self.validate(store['store_info']['corporate_id'])
      item['address'] = self.validate(store['store_info']['address'])
      item['address2'] = self.validate(store['store_info']['address_extended'])
      item['city'] = self.validate(store['store_info']['locality'])
      item['state'] = self.validate(store['store_info']['region'])
      item['zip_code'] = self.validate(store['store_info']['postcode'])
      item['country'] = self.validate(store['store_info']['country'])
      item['phone_number'] = self.validate(store['store_info']['phone'])
      item['latitude'] = self.validate(store['store_info']['latitude'])
      item['longitude'] = self.validate(store['store_info']['longitude'])
      h_temp = ''
      week_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
      hour_list = store['store_info']['store_hours'].split(';')
      for hour in hour_list:
        try:
          hour = hour.split(',')
          h_temp += week_list[int(hour[0])-1] + ' ' + hour[1][:2] + ':' + hour[1][2:]
          h_temp += '-' + hour[2][:2] + ':' + hour[2][2:] + ', '
        except:
          pass
      item['store_hours'] = h_temp[:-2]
      yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''