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
import unicodedata
import usaddress
import pdb
class dunnbroscoffee(scrapy.Spider):
  name = 'dunnbroscoffee'
  domain = ''
  history = []

  def start_requests(self):
    init_url = 'https://dunnbrothers.com/wp-content/plugins/store-locator/sl-xml.php'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    # print("=========  Checking.......")
    store_list = response.xpath('//marker')
    pdb.set_trace()
    for store in store_list:
      item = ChainItem()
      item['store_name'] = self.validate(store.xpath('./@name'))
      item['address'] = self.validate(store.xpath('./@street'))
      item['address2'] = self.validate(store.xpath('./@street2'))
      item['city'] = self.validate(store.xpath('./@city'))
      item['state'] = self.validate(store.xpath('./@state'))
      item['zip_code'] = self.validate(store.xpath('./@zip'))
      item['country'] = 'United States'
      item['phone_number'] = self.validate(store.xpath('./@phone'))
      item['latitude'] = self.validate(store.xpath('./@lat'))
      item['longitude'] = self.validate(store.xpath('./@lng'))
      h_temp = ''
      hour_list = self.validate(store.xpath('./@hours')).split('||sl-nl||')
      for hour in hour_list:
        if hour != '':
          h_temp += hour + ', '			
      item['store_hours'] = h_temp[:-2]
      yield item			

  def validate(self, item):
    try:
      return item.extract_first().strip().replace(';','')
    except:
      return ''

