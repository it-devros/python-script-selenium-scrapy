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


class LazboycSpider(scrapy.Spider):
  name = 'lazboy-c'
  request_url = 'http://www.la-z-boy.com/storeLocator/json/storeResultByCoordinates.jsp?latitude=%s&longitude=%s&distance=300008&sortOption=1'
  states = []
  uid_list = []

  def __init__(self):
    with open('states.json', 'r') as f:
      self.states = json.load(f)
  
  def start_requests(self):
    for state in self.states:
      url = self.request_url % (state['latitude'], state['longitude'])
      yield scrapy.Request(url=url, callback=self.parse_store)

  def parse_store(self, response):
    stores = json.loads(response.body)
    stores_list = stores[0]
    if stores_list['map']:
      for store in stores_list['map']:
        temp_store_number = store['storeID']
        if not temp_store_number in self.uid_list:
          self.uid_list.append(temp_store_number)
          item = ChainItem()

          item['store_name'] = store['storename']
          item['store_number'] = store['storeID']
          item['address'] = store['address1']
          item['address2'] = store['address2']
          item['city'] = store['city']
          item['state'] = store['state']
          item['zip_code'] = store['zip']
          if store['country'] == 'US':
            item['country'] = 'United States'
          else:
            item['country'] = store['country']
          item['store_type'] = store['storetype']
          item['longitude'] = store['longi']
          item['latitude'] = store['lat']
          item['phone_number'] = store['phone']

          yield item
        else:
          print("++++++++++++++++++++++++++ aready scraped")

