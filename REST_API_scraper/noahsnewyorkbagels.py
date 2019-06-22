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

class noahsnewyorkbagels(scrapy.Spider):
  name = 'noahsnewyorkbagels'
  domain = ''
  history = []

  def __init__(self):
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/cities.json'
    with open(file_path) as data_file:
      self.location_list = json.load(data_file)

  def start_requests(self):
    for location in self.location_list:
      init_url = 'https://api.donde.io/near?callback=jQuery1102032769694189069765_1494000277537&center='+str(location['latitude'])+','+str(location['longitude'])+'&limit=500&dondeKey=571eb1bea06e660017000032'
      yield scrapy.Request(url=init_url, callback=self.body)

  def body(self, response):
    print("=========  Checking.......")
    store_list = json.loads(response.body.split('jQuery1102032769694189069765_1494000277537(')[1][:-2])
    for store in store_list:
      item = ChainItem()
      item['store_name'] = store['name']
      item['store_number'] = store['corporate_id']
      item['address'] = store['street']
      item['address2'] = store['address_line_2']
      item['city'] = store['city']
      item['state'] = store['state']
      item['zip_code'] = store['zip']
      item['country'] = store['country']
      item['phone_number'] = store['phone']
      item['latitude'] = store['Location']['coordinates'][0]
      item['longitude'] = store['Location']['coordinates'][1]
      week_list = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
      h_temp = ''
      hour_list = store['formatted_hours']
      for hour in hour_list:
        h_temp += week_list[int(hour['day_of_week'])] +' ' + hour['open_time'] + ' ' + hour['close_time'] + ', '
      item['store_hours'] = h_temp[:-2]
      item['store_type'] = ''
      item['other_fields'] = ''
      item['coming_soon'] = ''
      if item['store_number'] not in self.history:
        self.history.append(item['store_number'])
        yield item

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''
