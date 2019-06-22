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

class vector(scrapy.Spider):
  name = 'vector'
  domain = 'http://www.vetcor.com'
  history = []

  def start_requests(self):
    init_url = 'http://www.vetcor.com/our-practices'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    store_links = response.xpath('//li[@class="drop"]//div//ul//li//a')
    for store_link in store_links:
      request_url = store_link.xpath('./@href').extract_first()
      request = scrapy.Request(url=request_url, callback=self.parse_store)
      request.meta['store'] = store_link.xpath('./text()').extract_first()
      request.meta['url'] = request_url
      yield request

  def parse_store(self, response):
    store_info = response.xpath('//div[@itemprop="articleBody"]//h1/text()').extract_first()
    store_name = ''
    try:
      store_name = self.getStoreName(store_info)
    except:
      pass
    if store_name:
      temp_address = response.xpath('//footer[@id="footer"]//address')[0]
      full_address = self.validate(temp_address.xpath('./span/text()').extract_first())
      phone = self.validate(response.xpath('//div[@class="contact-holder"]/a/text()').extract_first())
      if full_address.find('phone') != -1:
        full_address = self.validate(temp_address.xpath('./text()').extract_first())
      last_char = response.meta['url'][-1:]
      added_link = response.xpath('//li[@class="timings"]//a/@href').extract_first()
      if not added_link:
        added_link = response.xpath('//li[@class="timing"]//a/@href').extract_first()
      timing_link = ''
      if last_char == '/':
        timing_link = response.meta['url'][:-1] + added_link
      else:
        timing_link = response.meta['url'] + added_link
      request = scrapy.Request(url=timing_link, callback=self.parse_hour)
      request.meta['store_name'] = store_name
      request.meta['address'] = ''
      request.meta['city'] = ''
      addr = usaddress.parse(full_address)
      for temp in addr:
        if temp[1] == 'PlaceName':
          request.meta['city'] += temp[0].replace(',','')	+ ' '
        elif temp[1] == 'StateName':
          request.meta['state'] = temp[0]
        elif temp[1] == 'ZipCode':
          request.meta['zip_code'] = temp[0].replace(',','')
        else:
          request.meta['address'] += temp[0].replace(',', '') + ' '
      request.meta['phone_number'] = phone
      yield request
    else:
      store_info = response.meta['store']
      item = ChainItem()
      item['store_name'] = self.getStoreInfo(store_info)[0]
      item['city'] = self.getStoreInfo(store_info)[1]
      item['state'] = self.getStoreInfo(store_info)[2]
      yield item
  
  def parse_hour(self, response):
    store_hour = response.xpath('//div[@itemprop="articleBody"]//table//tbody//tr//td/text()').extract()
    print store_hour
    hours = ''
    for hour in store_hour:
      hours += self.validate(hour) + ' '
    item = ChainItem()
    item['store_name'] = response.meta['store_name']
    item['address'] = response.meta['address']
    item['city'] = response.meta['city']
    item['state'] = response.meta['state']
    item['zip_code'] = response.meta['zip_code']
    item['phone_number'] = response.meta['phone_number']
    item['store_hours'] = hours
    yield item

  def getStoreInfo(self, item):
    info = ['', '', '']
    item_list = item.split(',')
    info[2] = self.validate(item_list[1])
    item = item_list[0]
    item_list = item.split('-')
    info[0] = self.validate(item_list[0])
    info[1] = self.validate(item_list[1])
    return info
    
  def validate(self, item):
    try:
      item = self.format(item)
      return item.strip()
    except:
      return ''

  def getStoreName(self, item):
    if item.find('Welcome to') != -1:
      item = item.replace('Welcome to', '').replace('!', '')
      return self.validate(item)
    else:
      return ''

  def format(self, item):
    try:
      return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
    except:
      return ''