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

class gordonfoodservice(scrapy.Spider):
  name = 'gordonfoodservice'
  domain = 'https://www.gfs.com/en'
  history = []

  def start_requests(self):
    init_url = 'https://www.gfs.com/en/service/locations/store'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    store_list = json.loads(response.body)
    if store_list:
      for store in store_list:
        item = ChainItem()
        if store['title']:
          item['store_name'] = store['title']
        if store['field_address']:
          item['country'] = store['field_address'][0]['country']
          item['state'] = store['field_address'][0]['administrative_area']
          item['city'] = store['field_address'][0]['locality']
          item['zip_code'] = store['field_address'][0]['postal_code']
          item['address'] = store['field_address'][0]['thoroughfare']
        if store['field_hours']:
          item['store_hours'] = self.validateHours(store['field_hours'][0]['value'])
        if store['field_latitude']:
          item['latitude'] = store['field_latitude'][0]['value']
        if store['field_longitude']:
          item['longitude'] = store['field_longitude'][0]['value']
        if store['field_number']:
          item['store_number'] = store['field_number'][0]['value']
        if store['field_phone']:
          item['phone_number'] = store['field_phone'][0]['value']
        yield item
    else:
      pass

  def validateHours(self, item):
    try:
      return item.replace('<p>', '').replace('<br>', '').replace('</p>', '').replace('\r', '').replace('\n', '').replace('\t', ', ').strip()
    except:
      return ''

  def format(self, item):
    try:
      return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
    except:
      return ''