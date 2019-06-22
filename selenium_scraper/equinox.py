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
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class EquinoxSpider(scrapy.Spider):
  name = 'equinox'
  domain = 'https://www.equinox.com'
  start_url = 'https://www.equinox.com/clubs?icmp=topnav-clubs'

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver.exe")

  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_regions)

  def parse_regions(self, response):
    url = self.start_url
    self.driver.get(url)
    time.sleep(2)
    source = self.driver.page_source.encode("utf8")
    tree = etree.HTML(source)
    stores_link = tree.xpath('//div[@class="region-list"][@data-component="region-list"]//ul//li//a/@href')
    print(stores_link)
    
    for store_link in stores_link:
      if store_link.find('https') == -1 and store_link.find('canada') == -1:
               
        request_url = self.domain + store_link
        self.driver.get(request_url)
        time.sleep(2)
        source_store = self.driver.page_source.encode("utf8")
        tree_store = etree.HTML(source_store)
        stores = tree_store.xpath('//div[@class="club-detail club-detail-region"]')
        for store in stores:
          store_name = store.xpath('./h3[@class="club-title"]/text()')[0]
          address = store.xpath('.//div[@class="club-body"]//div[@class="club"]//p/text()')[0]
          hours_label = store.xpath('.//div[@class="club-body"]//div[@class="club-hours"]//div[@class="period"]//span[@class="day-name"]//strong/text()')
          hours = store.xpath('.//div[@class="club-body"]//div[@class="club-hours"]//div[@class="period"]//span/text()')
          phone = store.xpath('.//div[@class="club-body"]//div[@class="club"]//p//a/text()')[0]
          address = address.strip()
          addr_list = address.split(', ')
          addr = ''
          city = ''
          state = ''
          zip_code = ''
          i = 0
          for addr_li in addr_list:
            i += 1
          print(i)
          if i == 3:
            addr = addr_list[0]
            city = addr_list[1]
            state_zip = addr_list[2]
            addr_list = state_zip.split(' ')
            state = addr_list[0]
            zip_code = addr_list[1][:-1]
          elif i == 4:
            addr = addr_list[0] + ' ' + addr_list[1]
            city = addr_list[2]
            state_zip = addr_list[3]
            addr_list = state_zip.split(' ')
            state = addr_list[0]
            zip_code = addr_list[1][:-1]
          item = ChainItem()
          item['store_name'] = store_name
          item['address'] = addr
          item['city'] = city
          item['state'] = state
          item['zip_code'] = zip_code
          if phone == 'COMING SOON':
            item['coming_soon'] = '1'
          else:
            item['coming_soon'] = '0'
            item['phone_number'] = phone
            i = 0
            store_hour = ''
            for hour_label in hours_label:
              store_hour += hour_label + ' ' + hours[i] + '; '
              i += 1
            item['store_hours'] = store_hour
          
          yield item


