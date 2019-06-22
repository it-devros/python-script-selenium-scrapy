import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class BigySpider(scrapy.Spider):
  name = 'bigy'
  domain = 'https://www.bigy.com'
  request_url = 'https://bigy.myrelationshop.com/Sysnify.Relationshop.v2/StoreLocation/SearchStore'

  def start_requests(self):
    url = self.request_url
    yield scrapy.Request(url=url, callback=self.parse_stores)

  def parse_stores(self, response):
    if response.body:
      _response = response.body
      stores_list = _response.split('var stores = [')
      stores_str = stores_list[1]
      stores_list = stores_str.split('];')
      stores_str = stores_list[0]
      store_list = stores_str.split('},{')
      for store in store_list:
        item = ChainItem()
        store_li = store.split('"Active":')
        store = store_li[1]
        temp_list = store.split(',')
        if temp_list[0] == 'true':
          item['coming_soon'] = '0'
        else:
          item['coming_soon'] = '1'
        store_li = store.split('"Address1":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['address'] = temp_list[0]
        store_li = store.split('"Address2":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['address2'] = temp_list[0]
        store_li = store.split('"City":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['city'] = temp_list[0]
        store_li = store.split('"StoreName":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['store_name'] = temp_list[0]
        store_li = store.split('"StoreID":')
        store = store_li[1]
        temp_list = store.split(',')
        item['store_number'] = temp_list[0]
        store_li = store.split('"State":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['state'] = temp_list[0]
        store_li = store.split('"Zipcode":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['zip_code'] = temp_list[0]
        store_li = store.split('"PhoneNumber":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['phone_number'] = temp_list[0]
        store_li = store.split('"StoreHours":"')
        store = store_li[1]
        temp_list = store.split('",')
        item['store_hours'] = temp_list[0]
        store_li = store.split('"Latitude":')
        store = store_li[1]
        temp_list = store.split(',')
        item['latitude'] = temp_list[0]
        store_li = store.split('"Longitude":')
        store = store_li[1]
        temp_list = store.split(',')
        item['longitude'] = temp_list[0]
        item['country'] = 'United States'
        yield item
    else:
      print('+++++++++++++++++++++++++++++++ no response')
