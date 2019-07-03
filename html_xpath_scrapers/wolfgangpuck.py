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

class wolfgangpuck(scrapy.Spider):
  name = 'wolfgangpuck'
  domain = 'https://wolfgangpuck.com'
  history = []
  location_links = []

  def start_requests(self):
    init_url = 'https://wolfgangpuck.com'
    yield scrapy.Request(url=init_url, callback=self.body)

  def body(self, response):
    str_stores = self.getJsonString(response.body)
    str_stores = self.validateJsonString(str_stores)
    stores = json.loads(str_stores)
    self.location_links = response.xpath('//div[@class="locations_spinner"][@id="catering-venue-list"]//div//a')
    if stores:
      for store in stores:
        store_info = []
        store_info = self.getStoreInfo(self.getValidData(store['title']))
        if store_info[0] != '':
          request_url = store_info[0]
          request = scrapy.Request(url=request_url, callback=self.parse_store)
          request.meta['store_id'] = store_info[1]
          request.meta['lat'] = store_info[2]
          request.meta['lng'] = store_info[3]
          request.meta['country'] = self.getValidData(store['country'])
          request.meta['state'] = self.getValidData(store['state'])
          request.meta['city'] = self.getValidData(store['city'])
          request.meta['name'] = self.getValidData(store['title'])
          yield request
        else:
          pass
    else:
      pass
  
  def parse_store(self, response):
    temp = response.xpath('//section[@class="blockout venue"]//div[@class="blockout-ctr"]//p')
    temp_addr = self.validateList(temp[1].xpath('./text()').extract())
    zip_code = self.getZip(temp_addr[1])
    address = self.validate(temp_addr[0])
    a_list = temp[0].xpath('./span[@class="contact"]//a')
    phone = self.validate(a_list[1].xpath('./text()').extract_first())
    item = ChainItem()
    item['store_number'] = response.meta['store_id']
    item['latitude'] = response.meta['lat']
    item['longitude'] = response.meta['lng']
    item['country'] = response.meta['country']
    item['state'] = response.meta['state']
    item['city'] = response.meta['city']
    item['store_name'] = response.meta['name']
    item['address'] = address
    item['zip_code'] = zip_code
    item['phone_number'] = phone.replace('.', '-')
    yield item
  
  def getZip(self, item):
    try:
      if item:
        item = item.split(',')[1].strip()
        item = item.split('\t\t\t')[1].strip()
        return item
      else:
        return ''
    except:
      return 'an error zip'
  
  def getStoreInfo(self, item):
    if self.location_links:
      value = ['','','','']
      for link in self.location_links:
        link_text = link.xpath('./text()').extract_first().strip()
        if link_text == item:
          value[0] = link.xpath('./@href').extract_first().strip()
          value[1] = link.xpath('./@data-id').extract_first().strip()
          value[2] = link.xpath('./@data-lat').extract_first().strip()
          value[3] = link.xpath('./@data-long').extract_first().strip()
          break
      if value:
        return value
      else:
        return ['','','','']
    else:
      return ['','','','']
  
  def validateList(self, _list):
    if _list:
      i = 0
      count = len(_list)
      while i < count:
        _list[i] = _list[i].strip()
        i += 1
      return _list
    else:
      return []
  
  def getValidData(self, item):
    try:
      if item.find('N/A') != -1:
        return ''
      else:
        return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
    except:
      return ''
  
  def getJsonString(self, item):
    try:
      return item.split('all_restaurants = ')[1].split(';')[0].strip()
    except:
      return ''
  
  def validateJsonString(self, item):
    try:
      return item.replace('country', '"country"').replace('state', '"state"').replace('city', '"city"').replace('title', '"title"')
    except:
      return item

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''