import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import time
import re

class StaplesSpider(scrapy.Spider):
  name = 'staples'
  request_url = 'https://storelocator.staples.ca/stores.xml?latitude=%s&longitude=%s&radius=100&locale=en_CA&offset=0&limit=50'
  domain = 'https://storelocator.staples.ca/stores/en_CA/'
  cities = []
  uid_list = []
  canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.cities = json.load(f)

  def start_requests(self):
    for city in self.cities:
      if self.cities[city]['state'] in self.canada_state_list:
        url = self.request_url % (self.cities[city]['latitude'], self.cities[city]['longitude'])
        yield scrapy.Request(url=url, callback=self.parse_store)

  def parse_store(self, response):
    flag_success = response.xpath('//status/text()').extract_first()
    if flag_success == 'SUCCESS':
      stores = response.xpath('//store')
      if stores:
        for store in stores:
          temp_store_number = store.xpath('.//store_number/text()').extract_first()
          if not temp_store_number in self.uid_list:
            self.uid_list.append(temp_store_number)
            item_store = ['','','','','','','','','','']
            item_store[0] = temp_store_number
            item_store[1] = 'Store #' + temp_store_number
            item_store[2] = store.xpath('.//latitude/text()').extract_first()
            item_store[3] = store.xpath('.//longitude/text()').extract_first()
            item_store[4] = store.xpath('.//store_address//address_line1/text()').extract_first()
            item_store[5] = store.xpath('.//store_address//city/text()').extract_first()
            item_store[6] = store.xpath('.//store_address//state/text()').extract_first()
            item_store[7] = store.xpath('.//store_address//zip/text()').extract_first()
            item_store[8] = 'Canada'
            item_store[9] = store.xpath('.//store_address//phone_number/text()').extract_first()

            detail_url = self.domain + item_store[6] + '/' + item_store[5] + '/' + item_store[0]
            request =  scrapy.Request(url=detail_url, callback=self.parse_hours)
            request.meta['item_store'] = item_store
            yield request
          else:
            print('+++++++++++++++++++++++++ aready scraped')
      else:
        print('+++++++++++++++++++++++++++++++++ none recognized stores')
    else:
      print('+++++++++++++++++++++++++++++++++++++++++++ there is not stores')
  
  def parse_hours(self, response):
    item_store = response.meta['item_store']
    item = ChainItem()
    item['store_number'] = item_store[0]
    item['store_name'] = item_store[1]
    item['latitude'] = item_store[2]
    item['longitude'] = item_store[3]
    item['address'] = item_store[4]
    item['city'] = item_store[5]
    item['state'] = item_store[6]
    item['zip_code'] = item_store[7]
    item['country'] = item_store[8]
    item['phone_number'] = item_store[9]
    temp_hour = ''
    try:
      temp_hours_list = response.xpath('//div[@class="storeTime"]')
      if temp_hours_list[0]:
        temp_hour_array = temp_hours_list[0].xpath('.//div//span/text()').extract()
        for temp_hour_li in temp_hour_array:
          temp_result = temp_hour_li.strip()
          temp_hour += re.sub('\s+', '', temp_result) + '; '
      else:
        temp_hour = 'There are not store hours in this store detail'
        print('+++++++++++++++++++++++++++++++++++ none exist store hours')
    except:
      temp_hour = 'an error occupied for store hours'
      print('++++++++++++++++++++++++++++ store hours error')
    if temp_hour == '':
      temp_hour = 'There are not store hours in this store detail'
    
    item['store_hours'] = temp_hour

    yield item
        
