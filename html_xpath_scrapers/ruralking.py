import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html
import pdb

class ruralking(scrapy.Spider):
  name = 'ruralking'
  domain = 'https://www.ruralking.com'
  history = []
  pos_list = []

  def start_requests(self):
    init_url = 'https://www.ruralking.com/storelocator/index/loadstore'
    frmdata = {
      'address': '',
      'type': 'map'
    }
    
    yield FormRequest(url=init_url, callback=self.body, formdata=frmdata)

  def body(self, response):
    self.pos_list = json.loads(response.body)
    init_url = 'https://www.ruralking.com/storelocator/index/loadstore/'
    frmdata = {
      'address': ''
    }
    
    yield FormRequest(url=init_url, callback=self.parse_store, formdata=frmdata)
  
  def parse_store(self, response):
    store_temp = etree.HTML(response.body)
    try:
      store_list = store_temp.xpath('//li[@class="item"]')
      for store in store_list:
        item = ChainItem()
        store_info = store.xpath('.//div[@class="info"]//p/text()')
        item['store_name'] = self.validateStoreName(store_info[0])
        temp_address = self.validate(store_info[1])
        item['address'] = self.stringToaddress(temp_address)[0]
        item['city'] = self.stringToaddress(temp_address)[1]
        item['state'] = self.stringToaddress(temp_address)[2]
        temp_string = self.validate(store_info[2])
        item['country'] = self.stringToaddress(temp_string)[0]
        item['zip_code'] = self.stringToaddress(temp_string)[1]
        item['phone_number'] = self.validate(store_info[3])
        item['store_hours'] = self.validate(store_info[4])
        item['store_number'] = self.stringToStoreNumber(item['store_name'])
        item['latitude'] = ''
        item['longitude'] = ''
        for pos in self.pos_list['stores']:
          if item['store_number'] == pos['storelocator_id']:
            item['latitude'] = pos['latitude']
            item['longitude'] = pos['longtitude']
        yield item
    except:
      print('====================================== an error')
      pass

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''
  
  def validateStoreName(self, item):
    try:
      item = item.replace('- NOW OPEN', '').strip()
      return item
    except:
      return item
  
  def stringToStoreNumber(self, item):
    try:
      item_list = item.split('#')
      return item_list[1].strip()
    except:
      return ['none', 'none']
  
  def stringToaddress(self, item):
    try:
      if item.find(',') != -1:
        item_list = item.split(',')
      else:
        item_list = item.split(' ')
      count = len(item_list)
      i = 0
      while i < count:
        item_list[i] = item_list[i].strip()
        i += 1
      return item_list
    except:
      return ['none', 'none', 'none']