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

class baskinrobbins(scrapy.Spider):
  name = 'baskinrobbins'
  domain = ''
  history = []

  def __init__(self):
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/US_CA_States.json'
    with open(file_path) as data_file:    
      self.location_list = json.load(data_file)

  def start_requests(self):
    for location in self.location_list:
      init_url = 'https://www.mapquestapi.com/search/v2/radius?callback=jQuery1112040290627844634885_1493995727767&key=Gmjtd%7Clu6t2luan5%252C72%253Do5-larsq&origin='+location['name']+'&units=m&maxMatches=500&ambiguities=ignore&radius=500&hostedData=mqap.33454_BaskinRobbins'
      yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    try:
      store_list = json.loads(response.body.split('jQuery1112040290627844634885_1493995727767(')[1].strip()[:-2])['searchResults']
      for store in store_list:
        item = ChainItem()
        item['store_name'] = store['fields']['n']
        item['store_number'] = store['fields']['recordid']
        item['address'] = store['fields']['address']
        item['address2'] = store['fields']['address2']
        item['city'] = store['fields']['city']
        item['state'] = store['fields']['state']
        item['zip_code'] = store['fields']['postal']
        item['country'] = store['fields']['country']
        item['phone_number'] = store['fields']['phonenumber']
        item['latitude'] = store['fields']['lat']
        item['longitude'] = store['fields']['lng']
        if store['fields']['mon_hours'] != '':
          item['store_hours'] = 'Mon ' + store['fields']['mon_hours'] + ', '
          item['store_hours'] += 'Tue ' + store['fields']['tue_hours'] + ', '
          item['store_hours'] += 'Wed ' + store['fields']['wed_hours'] + ', '
          item['store_hours'] += 'Thu ' + store['fields']['thu_hours'] + ', '
          item['store_hours'] += 'Fri ' + store['fields']['fri_hours'] + ', '
          item['store_hours'] += 'Sat ' + store['fields']['sat_hours'] + ', '
          item['store_hours'] += 'Sun ' + store['fields']['sun_hours']
        if item['store_number'] not in self.history:
          self.history.append(item['store_number'])
          yield item		
    except:
      pass	

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''