import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class CartridgeworldSpider(scrapy.Spider):
  name = 'cartridgeworld'
  domain = 'https://www.cartridgeworld.com'
  request_url = 'https://www.cartridgeworld.com/store/search?SearchQuery=%s&SourceLatitude=%s&SourceLongitude=%s'
  store_stack = []
  us_location_list = []
  ca_location_list = []
  ca_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
  us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

  def __init__(self):
    
    with open('US_Cities.json', 'rb') as data_file:    
      self.us_location_list = json.load(data_file)

    with open('CA_Cities.json', 'rb') as data_file:    
      self.ca_location_list = json.load(data_file)

  def start_requests(self):
    for location in self.us_location_list:
      url = self.request_url % (location['city'].replace(' ', '+'), location['latitude'], location['longitude'])
      yield scrapy.Request(url=url, callback=self.body)
    
    for location in self.ca_location_list:
      url = self.request_url % (location['city'].replace(' ', '+'), location['latitude'], location['longitude'])
      yield scrapy.Request(url=url, callback=self.body)

  def body(self, response):
    print('============================= Checking..........')
    stores_list = []
    try:
      stores_list = response.xpath('//li[@class="js-store-box"]//div[@class="store-box-inner"]')
    except:
      print('================================= no stores list')
      stores_list = []
    if stores_list:
      for store in stores_list:
        latitude = store.xpath('./input[@class="js-store-latitude"]/@value').extract_first()
        longitude = store.xpath('./input[@class="js-store-longitude"]/@value').extract_first()
        store_name = store.xpath('./a[@class="store-title"]/text()').extract_first()
        phone = store.xpath('./dl/dd/a/text()').extract_first()
        if not phone in self.store_stack:
          self.store_stack.append(phone)
          detail_link = self.domain + store.xpath('./a[@class="store-title"]/@href').extract_first()
          addr_list = store.xpath('.//dl//dd/text()').extract()
          i = 0
          for addr in addr_list:
            i += 1
          j = 0
          address = ''
          while j < i - 1:
            address += addr_list[j] + ' '
            j += 1
          csz = addr_list[i - 1]
          csz_list = csz.split(', ')
          city = csz_list[0]
          csz = csz_list[1]
          csz_list = csz.split(' ')
          i = 0
          for csz in csz_list:
            i += 1
          state = csz_list[0]
          j = 1
          zip_code = ''
          while j < i:
            zip_code += csz_list[j] + ' '
            j += 1
          
          
          request = scrapy.Request(url=detail_link, callback=self.body_detail)
          request.meta['latitude'] = latitude
          request.meta['longitude'] = longitude
          request.meta['store_name'] = store_name
          request.meta['phone'] = phone
          request.meta['address'] = address
          request.meta['city'] = city
          request.meta['state'] = state
          request.meta['zip_code'] = zip_code

          yield request
        else:
          print('=========================================== already crawled')

    else:
      print('======================================== can not scrape')

  def body_detail(self, response):
    hours_list = []
    try:
      hours_list = response.xpath('//dl[@class="store-details-hours clearfix"]//dd//p/text()').extract()
    except:
      print('================================= store hours error')
      hours_list = []
    hours = ''
    if hours_list:
      for hour in hours_list:
        hours += hour.strip() + '; '
      print hours
    else:
      print('==================================== no store hours')
    item = ChainItem()
    item['latitude'] = response.meta['latitude']
    item['longitude'] = response.meta['longitude']
    item['store_name'] = response.meta['store_name']
    item['phone_number'] = response.meta['phone']
    item['address'] = response.meta['address']
    item['city'] = response.meta['city']
    item['state'] = response.meta['state']
    item['zip_code'] = response.meta['zip_code']
    item['store_hours'] = hours
    if item['store_hours']:
      item['coming_soon'] = '0'
    else:
      item['coming_soon'] = '1'
    
    if item['state'] in self.us_state_list:
      item['country'] = 'United States'
    elif item['state'] in self.ca_state_list:
      item['country'] = 'Canada'
    else:
      item['country'] = 'Puerto Rico'
    
    yield item
    