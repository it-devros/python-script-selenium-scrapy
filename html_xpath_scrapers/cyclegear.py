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

class cyclegear(scrapy.Spider):
  name = 'cyclegear'
  domain = 'https://www.cyclegear.com'
  history = []

  def start_requests(self):
    
    init_url = 'https://www.cyclegear.com/store-location'
    yield scrapy.Request(url=init_url, callback=self.body)

  def body(self, response):
    store_list = response.xpath('//a[@class="store-location-directory__store-city"]//@href').extract()
    for store in store_list:
      store_url = self.domain + store
      yield scrapy.Request(url=store_url, callback=self.parse_page)

  def parse_page(self, response):
  
    item = ChainItem()
    detail = response.xpath('//section[contains(@class, "store-show__address")]//text()').extract()
    item['store_name'] = ''
    item['store_number'] = ''
    item['address'] = self.validate(detail[0])
    item['address2'] = ''
    item['city'] = ''
    if len(detail) == 10:
      item['address2'] = self.validate(detail[1].split(',')[0])
      item['city'] = self.validate(detail[2].split(',')[0])
      item['state'] = self.validate(detail[2].split(',')[1])
      item['zip_code'] = self.validate(detail[3])
      item['country'] = 'United States'
      item['phone_number'] = self.validate(detail[8])
    else :
      item['city'] = self.validate(detail[1].split(',')[0])
      item['state'] = self.validate(detail[1].split(',')[1])
      item['zip_code'] = self.validate(detail[2])
      item['country'] = 'United States'
      item['phone_number'] = self.validate(detail[7])
    h_temp = ''
    hour_list = response.xpath('//section[contains(@class, "store-show__hours")]//table//tr')
    for hour in hour_list:
      time = hour.xpath('./td/text()').extract()
      if len(time) == 2:
        h_temp += self.validate(time[0]) + ' ' +  self.validate(time[1]) + ', '
      else:	
        h_temp += self.validate(time[0]) + ' ' +  self.validate(time[1]) + '-' + self.validate(time[2]) + ', '
    item['store_hours'] = h_temp[:-2]
    yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return '' 