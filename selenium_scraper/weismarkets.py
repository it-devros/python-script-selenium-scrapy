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
import requests
import string
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class WeismarketsSpider(scrapy.Spider):
  name = 'weismarkets'
  request_url = 'https://www.weismarkets.com/stores#/?page=1&pagesize=500'
  store_url = 'https://www.weismarkets.com/stores#/'
  domain = 'https://www.weismarkets.com/'
  uid_list = []

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver.exe")

  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_home)

  def parse_home(self, response):
    url = self.domain
    self.driver.get(url)
    time.sleep(2)
    url = self.request_url
    self.driver.get(url)
    time.sleep(2)
    source = self.driver.page_source.encode("utf8")
    tree = etree.HTML(source)
    
    stores_li = tree.xpath('.//ul[@class="location-list"]//li')
    if stores_li:
      printable = set(string.printable)
      for store in stores_li:
        temp_store_class = store.xpath('./@class')[0]
        temp_store_class_str = temp_store_class.split(' ')
        store_number = temp_store_class_str[1]
        if not store_number in self.uid_list:
          self.uid_list.append(store_number)
          detail_url = self.store_url + store_number
          self.driver.get(detail_url)
          time.sleep(1)
          source_detail = self.driver.page_source.encode("utf8")
          tree_detail = etree.HTML(source_detail)

          item = ChainItem()
          
          store_name = tree_detail.xpath('//div[@class="store-name"]/text()')[0]
          store_name_temp = store_name.strip()
          store_name_list = store_name_temp.split('#')
          item['store_name'] = store_name_list[0]
          item['store_number'] = store_name_list[1]
          store_address = tree_detail.xpath('//div[@class="store-address"]/text()')[0]
          item['address'] = store_address.strip()
          city_state = tree_detail.xpath('//div[@class="store-address"]/text()')[1]
          city_state_list = city_state.split(', ')
          item['city'] = city_state_list[0].strip()
          item['state'] = city_state_list[1].strip()
          zip_code = tree_detail.xpath('//div[@class="store-address"]/text()')[2]
          item['zip_code'] = zip_code.strip()
          item['country'] = 'United States'
          try:
            list_xpath = tree_detail.xpath('//div[@class="row columns-container"]//div[@class="col-xs-12"]//div[@class="content"]//table//tbody//tr')
            phone_number = list_xpath[8].xpath('.//td/text()')
            item['phone_number'] = phone_number[1]
          except:
            item['phone_number'] = ''
            print('+++++++++++++++++++++++++++++++++++ an error of store phone number')
           
          temp_hours = ''
          hours_xpath = []
          try:
            hours_xpath = tree_detail.xpath('//div[@class="container"]//div[@class="row columns-container"]//div[@class="col-xs-12"]//div[@class="content"]//table//tbody')
            if not hours_xpath:
              hours_xpath = tree_detail.xpath('//div[@class="hours-and-contact container"]//div[@class="row columns-container"]//div[@class="col-xs-12"]//div[@class="content"]//table//tbody')
          except:
            item['store_hours'] = 'an no store hours'
            print('++++++++++++++++++++++++++++++++++++ an error of store hours')

          if hours_xpath:
            hours = hours_xpath[0].xpath('.//tr')
            if hours:
              for hour in hours:
                temp_hours_str = hour.xpath('.//td/text()')
                temp_hours += temp_hours_str[0] + ' '
                temp_time = filter(lambda x: x in printable, temp_hours_str[1])
                temp_hours += temp_time
                temp_hours += '; '
              item['store_hours'] = temp_hours
            else:
              item['store_hours'] = 'do not have any hours'
              print('++++++++++++++++++++++++++++ do not have any hours')
          
          yield item
        else:
          print('+++++++++++++++++++++++++++++++++++ already scraped')
        
    else:
      print('+++++++++++++++++++++++++++++++++ there are not stores')

    self.driver.close()

  