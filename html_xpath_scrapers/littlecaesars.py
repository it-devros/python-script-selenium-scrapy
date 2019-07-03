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
import re

class LittlecaesarsSpider(scrapy.Spider):
  name = 'littlecaesars'
  request_url = 'http://www.littlecaesars.ca/Locations/tabid/89/Address/%s/PageNo/1/Default.aspx'
  cities = []
  uid_list = []
  canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.cities = json.load(f)

  def start_requests(self):
    for city in self.cities:
      if self.cities[city]['state'] in self.canada_state_list:
        url = self.request_url % (self.cities[city]['city'])
        request =  scrapy.Request(url=url, callback=self.parse_stores)
        request.meta['page_num'] = 1
        yield request
    

  def parse_stores(self, response):
    stores = response.xpath('//div[@class="lilsite lilsite-store-listing"]/ul/li')
    
    if stores:
      for store in stores:
        temp_addr_list = store.xpath('./ul/li/text()').extract()
        temp_city_state_zip = temp_addr_list[1]
        temp_city_state_zip_list = temp_city_state_zip.split(', ')
        temp_city = temp_city_state_zip_list[0]
        temp_city_state_zip = temp_city_state_zip_list[1]
        temp_city_state_zip_list = temp_city_state_zip.split(' ')
        temp_state = temp_city_state_zip_list[0]
        temp_zip = temp_city_state_zip_list[1] + temp_city_state_zip_list[2]
        if not temp_zip in self.uid_list:
          self.uid_list.append(temp_zip)
          item = ChainItem()
          temp_name = store.xpath('./ul/li/h2/a/text()').extract_first()
          item['store_name'] = temp_name
          item['address'] = temp_addr_list[0]
          item['city'] = temp_city
          item['state'] = temp_state
          item['zip_code'] = temp_zip
          item['phone_number'] = store.xpath('./ul/li/a/text()').extract_first()
          item['country'] = 'Canada'
          yield item
        else:
          print('++++++++++++++++++++++++++++++++++++++ already scraped')
    else:
      print('++++++++++++++++++++++++++++ stores not exist.')
    
    page_num = response.meta['page_num']
    pagination_num = response.xpath('//div[@class="lilsite-pager"]//ol[@class="pagers"]//li//a/text()')
    page_count = 0
    for pagi in pagination_num:
      page_count += 1
    print(page_count)
    if page_count >= page_num:
      next_num = page_num + 1
      url = 'http://www.littlecaesars.ca/Locations/tabid/89/Address/vancouver/PageNo/' + str(next_num) + '/Default.aspx'
      request = scrapy.Request(url=url, callback=self.parse_stores)
      request.meta['page_num'] = next_num
      yield request

    