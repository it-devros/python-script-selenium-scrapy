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

class milestonesgrillandbar(scrapy.Spider):
  name = 'milestonesgrillandbar'
  domain = ''
  history = []
  count = 0
  def start_requests(self):
    init_url = 'http://www.milestonesrestaurants.com/location_region.php'
    yield scrapy.Request(url=init_url, callback=self.parse_state) 

  def parse_state(self, response):
    print("=========  Checking.......")
    state_list = response.xpath('//select[@id="province"]//option/@value').extract()
    for state in state_list:
      if state !='none':
        state_url = 'http://www.milestonesrestaurants.com/location_get_city.php?province=%s' %state
        yield scrapy.Request(url=state_url, callback=self.parse_city, meta={'state':state})

  def parse_city(self, response):
    city_list = response.xpath('//option/@value').extract()
    for city in city_list:
      if city !='none':
        city_url = 'http://www.milestonesrestaurants.com/location_region.php?province=%s&s=1&city_drop=%s' %(response.meta['state'], city)
        yield scrapy.Request(url=city_url, callback=self.parse_store)
  
  def parse_store(self, response):
    store_list = response.xpath('//ul[contains(@class, "services")]//li')
    for store in store_list:
      item = ChainItem()
      tmp = store.xpath('.//span/text()').extract()
      item['address'] = ''
      for t in tmp:
        item['address'] += self.validate(t)
      address = self.validate(store.xpath('.//p[1]/text()').extract_first()).split(',')
      item['city'] = self.validate(address[0])
      item['state'] = self.validate(address[1])
      item['zip_code'] = self.validate(address[2])
      item['country'] = 'Canada'
      item['phone_number'] = self.validate(store.xpath('.//p[1]//a/text()').extract_first())
      h_temp = ''
      hour_list = store.xpath('.//p[4]/text()').extract()
      for hour in hour_list:
        h_temp += self.validate(hour) + ', ' 
      item['store_hours'] = h_temp[:-2]
      yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''