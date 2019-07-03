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

class casualmalexl(scrapy.Spider):
  name = 'casualmalexl'
  domain = ''
  history = []

  def __init__(self):
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/cities.json'
    with open(file_path) as data_file:    
      self.location_list = json.load(data_file)

  def start_requests(self):
    for location in self.location_list:
      init_url = 'http://casual-male-big-and-tall.destinationxl.com/mens-big-and-tall-store/storelocator/storeList.jsp?lat='+str(location['latitude'])+'&lng='+str(location['longitude'])+'&radius=100&selectedstore=Destination%20XL,Casual%20Male%20XL&requestType=undefined'
      yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    with open('response.html', 'wb') as f:
      f.write(response.body)
    store_list = response.xpath('//marker')	
    for store in store_list:
      item = ChainItem()
      detail = self.validate(store.xpath('./@number')).split(' ')
      item['store_name'] = ''
      for cnt in range(0, len(detail)-1):
        item['store_name'] += detail[cnt]
      item['store_number'] = detail[len(detail)-1]
      item['address'] = self.validate(store.xpath('./@address'))
      item['address2'] = self.validate(store.xpath('./@address2'))
      item['city'] = self.validate(store.xpath('./@city'))
      item['state'] = self.validate(store.xpath('./@state'))
      item['zip_code'] = self.validate(store.xpath('./@postalcode'))
      item['country'] = 'United States'
      item['phone_number'] = self.validate(store.xpath('./@phoneNumber'))
      item['latitude'] = self.validate(store.xpath('./@lat'))
      item['longitude'] = self.validate(store.xpath('./@lng'))
      item['store_hours'] = self.validate(store.xpath('./@hours'))
      item['store_type'] = ''
      item['other_fields'] = ''
      item['coming_soon'] = ''
      if item['store_number'] not in self.history:
        self.history.append(item['store_number'])
        yield item			

  def validate(self, item):
    try:
      return item.extract_first().strip().replace('+', ' ').replace('%2C', ', ')
    except:
      return ''