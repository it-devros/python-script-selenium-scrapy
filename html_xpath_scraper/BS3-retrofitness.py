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
import time
import pdb

class retrofitness(scrapy.Spider):
  name = 'retrofitness'
  domain = 'https://www.retrofitness.com/'
  history = []

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver")
    script_dir = os.path.dirname(__file__)
    file_path = script_dir + '/geo/US_States.json'
    with open(file_path) as data_file:    
      self.location_list = json.load(data_file)

  def start_requests(self):
    
    init_url  = 'http://retrofitness.com/locator/'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    print("=========  Checking.......")
    store_list = []
    for location in self.location_list:
      try :
        self.driver.get("http://retrofitness.com/locator/")
        time.sleep(2)
        input = self.driver.find_element_by_id('bh-sl-address')
        input.clear()
        input.send_keys(location['name'])
        self.driver.find_element_by_class_name('btn-find-button').click()
        time.sleep(2)
        source = self.driver.page_source.encode("utf8")
        tree = etree.HTML(source)
        data = tree.xpath('//div[@class="loc-web"]//a/@href')
        for dat in data:
          store_list.append(dat)
      except:
        pass

    for store in store_list:
      print('~~~~~~~~~~~~~~``````', store)
      yield scrapy.Request(url=store, callback=self.parse_page)

  def parse_page(self, response):
    try:
      item = ChainItem()
      item['store_name'] = self.validate(response.xpath('//h1[@class="u-case"]//span[@itemprop="name"]/text()'))
      item['store_number'] = ''
      item['address'] = self.validate(response.xpath('//a[@class="main-address u-case"]//span[@itemprop="streetAddress"]/text()'))
      item['address2'] = ''
      item['city'] = self.validate(response.xpath('//a[@class="main-address u-case"]//span[@itemprop="addressLocality"]/text()'))
      item['state'] = self.validate(response.xpath('//a[@class="main-address u-case"]//span[@itemprop="addressRegion"]/text()'))
      zipcode = response.xpath('//a[@class="main-address u-case"]/text()').extract()
      item['zip_code'] = zipcode[len(zipcode)-1].split('|')[1].strip()
      item['country'] = 'United States'
      item['phone_number'] = self.validate(response.xpath('//span[@itemprop="telephone"]/text()'))
      item['latitude'] = ''
      item['longitude'] = ''
      h_temp = ''
      hour_list = response.xpath('//div[@class="day-hours-container"]//div[contains(@class, "day-hours-circle")]')
      for hour in hour_list:
        time = hour.xpath('.//div[@class="day-hours-bottom"]//div/text()').extract()
        h_temp += self.validate(hour.xpath('.//div[@class="day-hours-top"]//div/text()')) + ' '
        h_temp += time[0] + '-' + time[1] + ', '
      item['store_hours'] = h_temp[:-2]
      item['store_type'] = ''
      item['other_fields'] = ''
      item['coming_soon'] = ''
      if item['store_name']+str(item['phone_number']) not in self.history:
        self.history.append(item['store_name']+str(item['phone_number']))
        yield item			
    except:
      pass
      
  def validate(self, item):
    try:
      return item.extract_first().strip()
    except:
      return ''