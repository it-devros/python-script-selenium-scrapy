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

class abuelos(scrapy.Spider):
  name = 'abuelos'
  domain = ''
  history = []

  def start_requests(self):
    
    init_url = 'http://www.abuelos.com/locations/'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    store_list = response.xpath('//li//a/@href').extract()
    for store in store_list:
      yield scrapy.Request(url=store, callback=self.parse_page)

  def parse_page(self, response):
    detail = response.xpath('//section[@class="secondary small"]')
    item = ChainItem()
    item['store_name'] = self.validate(detail.xpath('.//h2[@class="condensed"]/text()'))
    item['address'] = self.validate(detail.xpath('.//address//span[@class="street"]/text()'))
    item['city'] = self.validate(detail.xpath('.//address//span[@class="city"]/text()'))
    item['state'] = self.validate(detail.xpath('.//address//span[@class="state"]/text()'))
    item['zip_code'] = self.validate(detail.xpath('.//address//span[@class="zip"]/text()'))
    item['country'] = 'United States'
    item['phone_number'] = self.validate(detail.xpath('.//a[@class="tel"]/text()'))
    h_temp = ''
    hour_list = detail.xpath('.//ul[@class="hours"]//li/text()').extract()
    for hour in hour_list:
      h_temp += hour.strip() + ' '
    item['store_hours'] = h_temp.strip()
    yield item			

  def validate(self, item):
    try:
      return item.extract_first().strip()
    except:
      return ''