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
import unicodedata

class blenzcoffee(scrapy.Spider):
  name = 'blenzcoffee'
  domain = ''
  history = []

  def start_requests(self):
    formdata = {
      'action':'store_wpress_listener',
      'method':'display_map',
      'page_number':'1',
      'lat':'49.264173',
      'lng':'-123.0804993,16',
      'category_id':'',
      'max_distance':'',
      'nb_display':'64'
    }
    header = {
      'Accept':'application/json, text/javascript, */*; q=0.01',
      'Accept-Encoding':'gzip, deflate',
      'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
      'X-Requested-With':'XMLHttpRequest'
    }
    init_url = 'http://blenz.com/wp-admin/admin-ajax.php'
    yield scrapy.FormRequest(url=init_url, method="POST", headers=header, formdata=formdata, callback=self.body) 

  def body(self, response):
    print("=========  Checking.......")
    store_list = json.loads(response.body)['locations']
    for store in store_list:
      
      item = ChainItem()
      item['store_name'] = store['name']
      item['store_number'] = ''
      address = store['address'].split(',')
      item['address'] = address[0]
      addr1 = address[1].split(' ')
      try:
        if len(addr1[len(addr1)-1]) == 2 or len(addr1[len(addr1)-1]) == 3:
          item['city'] = ''
          for i in range(0, len(addr1)-1):
            item['city'] += addr1[i] + ' '
          item['state'] = addr1[len(addr1)-1]
          item['zip_code'] = self.validate(address[2])
        else :
          item['city'] = address[1]
          item['state'] = address[2].strip().split(' ')[0].strip()
          item['zip_code'] = ''
          for cnt in range(1, len(address[2].strip().split(' '))):
            if address[2].strip().split(' ')[cnt] != 'Canada':
              item['zip_code'] += address[2].strip().split(' ')[cnt]
      except:
        item['city'] = addr1[1]
        item['state'] = addr1[2]
        item['zip_code'] = addr1[4]+addr1[5]
      item['country'] = 'Canada'
      item['phone_number'] = store['tel']
      item['latitude'] = store['lat']
      item['longitude'] = store['lng']
      h_temp = ''
      hour_list = etree.HTML(store['description']).xpath('//p//text()')
      for hour in hour_list:
        h_temp += self.validate(hour) + ' '
      item['store_hours'] = h_temp[:-2]
      yield item		


  def validate(self, item):
    try:

      return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
    except:
      return ''