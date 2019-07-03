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

class todo(scrapy.Spider):
  name = '7elevencanada'
  domain = 'https://www.7-eleven.com'
  history = []

  def __init__(self):
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/CA_Cities.json'
    with open(file_path) as data_file:    
      self.location_list = json.load(data_file)

  def start_requests(self):
    
    header={
      'Accept':'application/json, text/javascript, */*; q=0.01',
      'Accept-Encoding':'gzip, deflate, br',
      'Content-Type':'application/json',
      'X-Requested-With':'XMLHttpRequest'
    }
    init_url = 'https://www.7-eleven.com/sevenelevenapi/stores_V3/'
    for location in self.location_list:
      body = '{\
        "lat": "%s",\
        "lon": "%s",\
        "features": [],\
        "radius":"200",\
        "limit": "500"\
      }' % (str(location['latitude']), str(location['longitude']))
      yield scrapy.Request(url=init_url, method='post', body=body, headers=header, callback=self.body) 
  
  def body(self, response):
    print("=========  Checking.......")
    store_list = json.loads(response.body)
    for store in store_list:
      item = ChainItem()
      item['store_name'] = store['name']
      item['store_number'] = ''
      item['address'] = store['address']
      item['city'] = store['city']
      item['state'] = store['state']
      item['zip_code'] = store['zip']
      item['country'] = store['country']
      item['phone_number'] = store['phone']
      item['latitude'] = store['lat']
      item['longitude'] = store['lon']
      if item['phone_number'] not in self.history and item['country'] == 'CA':
        self.history.append(item['phone_number'])
        yield item			

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''