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

class rainbowshops(scrapy.Spider):
  name = 'rainbowshops'
  domain = 'www.rainbowshops.com'
  history = []

  def start_requests(self): 
    init_url = 'https://www.rainbowshops.com/on/demandware.store/Sites-rainbow-Site/default/Stores-GetNearestStores?postalCode=20010&countryCode=US&distanceUnit=mi&maxdistance=20000'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    valid_str = self.validate_(self.validate(response.body))
    store_list = json.loads(valid_str)
    if store_list:
      for store in store_list:
        item = ChainItem()
        item['store_number'] = self.validate(store_list[store]['storeID'])
        item['store_name'] = self.validate(store_list[store]['name'])
        item['address'] = self.validate(store_list[store]['address1'])
        item['address2'] = self.validate(store_list[store]['address2'])
        item['zip_code'] = self.validate(store_list[store]['postalCode'])
        item['city'] = self.validate(store_list[store]['city'])
        item['state'] = self.validate(store_list[store]['stateCode'])
        item['country'] = self.validate(store_list[store]['countryCode'])
        item['phone_number'] = self.validate(store_list[store]['phone'].replace('.', '-'))
        item['store_hours'] = self.validate(store_list[store]['storeHours'].replace('<br>', ', '))
        item['latitude'] = self.validate(store_list[store]['latitude'])
        item['longitude'] = self.validate(store_list[store]['longitude'])
        yield item
    else:
      pass

  def validate_(self, item):
    try:
      item_list = item.split('"distance":')
      total = len(item_list)
      i = 1
      temp_lat = item_list[0].split('"latitude": ')[1].split(',')[0]
      temp_lat1 = '"' + temp_lat + '"'
      item_list[0] = item_list[0].replace(temp_lat, temp_lat1)
      temp_lng = item_list[0].split('"longitude": ')[1].split(',')[0]
      temp_lng1 = '"' + temp_lng + '"'
      item_list[0] = item_list[0].replace(temp_lng, temp_lng1)
      value = item_list[0]
      while i < total:
        temp1 = item_list[i].split('}')[1]
        temp2 = '"distance": ' + '" "' + '}' + temp1
        temp3 = temp2
        try:
          temp_lat = temp2.split('"latitude": ')[1].split(',')[0]
          temp_lat1 = '"' + temp_lat + '"'
          temp2 = temp2.replace(temp_lat, temp_lat1)
          temp_lng = temp2.split('"longitude": ')[1].split(',')[0]
          temp_lng1 = '"' + temp_lng + '"'
          temp2 = temp2.replace(temp_lng, temp_lng1)
        except:
          temp2 = temp3
        value += temp2
        i += 1
      value = value + '}'
      return value
    except:
      return ''

  def validate(self, item):
    try:
      return item.replace('\n', '').strip()
    except:
      return ''