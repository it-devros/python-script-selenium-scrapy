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

class soulcycle(scrapy.Spider):
  name = 'soulcycle'
  domain = ''
  history = []

  def start_requests(self):
    init_url = 'https://www.soul-cycle.com/studios/all/'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    print("=========  Checking.......")
    store_list = response.xpath('//div[contains(@class, "studio-detail")]')
    for store in store_list:
      detail = store.xpath('.//p[@class="address"]')
      item = ChainItem()
      item['store_name'] = self.validate(detail.xpath('.//span[@class="name"]/text()').extract_first())
      address = detail.xpath('.//span[@class="street"]/text()').extract()
      item['address'] = self.validate(address[0])
      addr = address[1].strip().split(',')
      item['city'] = self.validate(addr[0].strip())
      item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
      item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
      item['country'] = 'United States'
      item['phone_number'] = self.validate(detail.xpath('.//span[@class="phone"]/text()').extract_first())
      try:
        zipcode = int(item['zip_code'])
        yield item			
      except:
        pass

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''