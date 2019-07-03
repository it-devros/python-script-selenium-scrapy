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
import usaddress

class wingzone(scrapy.Spider):
  name = 'wingzone'
  domain = ''
  history = []

  def __init__(self):
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/cities.json'
    with open(file_path) as data_file:    
      self.location_list = json.load(data_file)

  def start_requests(self):
    
    init_url = 'https://wingzone.com/locations/'
    yield scrapy.Request(url=init_url, callback=self.body) 
    # yield scrapy.Request(url='https://wingzone.com/stores/st-louis/', callback=self.parse_page)

  def body(self, response):
    store_list = response.xpath('//div[contains(@class,"store-info")]')
    for store in store_list:
      store_url = store.xpath('.//a/@href').extract_first()
      if store_url:
        yield scrapy.Request(url=store_url, callback=self.parse_page)
      else :
        item = ChainItem()
        item['store_name'] = self.validate(store.xpath('.//div[@class="box"]//h3//text()'))		
        address = self.validate(store.xpath('.//div[@class="box"]//p/text()'))
        addr = usaddress.parse(address)
        item['address'] = ''
        item['city'] = ''
        for temp in addr:
          if temp[1] == 'AddressNumber':
            item['address'] += temp[0] + ' '
          elif temp[1] == 'StreetName':
            item['address'] += temp[0] + ' '
          elif temp[1] == 'StreetNamePostType':
            item['address'] += temp[0] + ' '
          elif temp[1] == 'OccupancyType':
            item['address'] += temp[0] + ' '
          elif temp[1] == 'OccupancyIdentifier':	
            item['address'] += temp[0] + ' '
          elif temp[1] == 'PlaceName':
            item['city'] += temp[0]	+ ' '
          elif temp[1] == 'StateName':
            item['state'] = temp[0]
          elif temp[1] == 'ZipCode':
            item['zip_code'] = temp[0]
        item['country'] = 'United States'
        if item['city'] == '' :
          item['address'] = self.validate(store.xpath('.//div[@class="box"]//p/text()'))
          item['country'] = ''
        yield item


  def parse_page(self, response):
    detail = response.xpath('//div[contains(@class, "location-content")]')
    item = ChainItem()
    item['store_name'] = self.validate(detail.xpath('.//h3[@class="white"]/text()'))
    address = self.validate(detail.xpath('.//pre[@class="white"]/text()')).replace('.', ' ')
    addr = usaddress.parse(address)
    item['address'] = ''
    item['city'] = ''
    for temp in addr:
      if temp[1] == 'AddressNumber':
        item['address'] += temp[0] + ' '
      elif temp[1] == 'StreetName':
        item['address'] += temp[0] + ' '
      elif temp[1] == 'StreetNamePostType':
        item['address'] += temp[0] + ' '
      elif temp[1] == 'OccupancyType':
        item['address'] += temp[0] + ' '
      elif temp[1] == 'OccupancyIdentifier':	
        item['address'] += temp[0] + ' '
      elif temp[1] == 'PlaceName':
        item['city'] += temp[0]	+ ' '
      elif temp[1] == 'StateName':
        item['state'] = temp[0]
      elif temp[1] == 'ZipCode':
        item['zip_code'] = temp[0]
    item['country'] = 'United States'
    item['phone_number'] = self.validate(detail.xpath('.//p[@class="white"]/text()'))
    item['store_hours'] = self.validate(detail.xpath('.//div[contains(@class, "hours")]//pre/text()'))
    yield item			

  def validate(self, item):
    try:
      return item.extract_first().strip().replace('\n', ' ')
    except:
      return ''