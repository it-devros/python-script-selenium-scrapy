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

class chronictacos(scrapy.Spider):
  name = 'chronictacos'
  domain = 'http://www.chronictacos.com/'
  history = []

  def start_requests(self):
    
    url_list = ['us-locations', 'canada-locations']
    for url in url_list:
      init_url = self.domain + url
      yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    store_list = response.xpath('//a[@class="article-a btn"]/@href').extract()
    for store in store_list:
      store = 'http://' + store[2:]
      yield scrapy.Request(url=store, callback=self.parse_page)

  def parse_page(self, response):	
    item = ChainItem()
    detail = response.xpath('//address[@class="row-start"]')
    item['store_name'] = self.validate(detail.xpath('.//h3/text()'))
    try:
      item['address'] = self.validate(detail.xpath('.//p[@id="ctl01_rptAddresses_ctl00_pAddressInfo"]/text()'))[:-1]
      item['address2'] = self.validate(detail.xpath('.//p[@id="ctl01_rptAddresses_ctl00_pAddressInfoTwo"]/text()'))[:-1]
      addr = self.validate(detail.xpath('.//p[@id="ctl01_rptAddresses_ctl00_pStateZip"]/text()')).split(',')
      item['city'] = addr[0].strip()
      item['state'] = addr[1].strip().split(' ')[0].strip()
      item['zip_code'] = addr[1].strip().split(' ')[1].strip()
      try:
        zip_code = int(item['zip_code'])
        item['country'] = 'United States'
      except:
        item['country'] = 'Canada'	
      item['phone_number'] = self.validate(detail.xpath('.//p[@id="ctl01_rptAddresses_ctl00_pPhonenum"]/text()')).split('Phone.')[1].strip()
    except:
      item['address'] = self.validate(detail.xpath('.//p[1]/text()'))[:-1]
      item['address2'] = self.validate(detail.xpath('.//p[2]/text()'))[:-1]
      addr = self.validate(detail.xpath('.//p[@id="ctl01_rptAddresses_ctl00_pStateZip"]/text()')).split(',')
      item['city'] = addr[0].strip()
      item['state'] = addr[1].strip().split(' ')[0].strip()
      item['zip_code'] = addr[1].strip().split(' ')[1].strip()

    item['store_hours'] = self.validate(response.xpath('//div[@id="ctl01_pSpanDesc"]//p[1]/text()'))
    yield item	

  def validate(self, item):
    try:
      return item.extract_first().strip()
    except:
      return ''