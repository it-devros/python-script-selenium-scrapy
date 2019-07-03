import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class HmartSpider(scrapy.Spider):
  name = 'hmart'
  domain = 'http://nj.hmart.com'
  start_url = 'http://nj.hmart.com/stores/'

  def start_requests(self):
    url = self.start_url
    yield scrapy.Request(url=url, callback=self.parse_stores)
  
  def parse_stores(self, response):
    store_list = response.xpath('//li[@class="no-icon"]//a')
    if store_list:
      for store in store_list:
        request_url = store.xpath('./@href').extract_first()
        yield scrapy.Request(url=request_url, callback=self.parse_detail)
      # request_url = 'http://nj.hmart.com/stores/buena-park/'
      # yield scrapy.Request(url=request_url, callback=self.parse_detail)
    else:
      print('+++++++++++++++++++++++++++++++++ no stores')

  def parse_detail(self, response):
    store = response.xpath('//div[@class="store-detail clearfix"]')
    if store:
      store_name = store.xpath('./h1/text()').extract_first()
      store_info_list = store.xpath('./div[@class="store-info"]//div[@class="store-info-box"]')
      addr_info = store_info_list[0].xpath('./text()').extract()
      i = 0
      for addr in addr_info:
        i += 1
      address = ''
      city_state_zip = ''
      city = ''
      state = ''
      zip_code = ''
      if i > 2:
        address = addr_info[1].strip()
        city_state_zip = addr_info[2].strip()
        addr_list = city_state_zip.split(', ')
        city = addr_list[0]
        city_state_zip = addr_list[1]
        addr_list = city_state_zip.split(' ')
        state = addr_list[0]
        zip_code = addr_list[1]
      else:
        temp_str = addr_info[1].strip()
        addr_temp = temp_str.split(', ')
        address = addr_temp[0].strip()
        city = addr_temp[1].strip()
        state_zip = addr_temp[2].strip()
        addr_temp = state_zip.split(' ')
        state = addr_temp[0]
        zip_code = addr_temp[1]
      phone_info = store_info_list[1].xpath('./text()').extract()
      phone = phone_info[1].strip().replace('Tel:', '')
      hour_info_list = store_info_list[2].xpath('./text()').extract()
      hour = ''
      i = 0
      for hour_li in hour_info_list:
        hour_li = hour_li.strip()
        if i != 0:
          hour += hour_li + '; '
        i += 1
      geo_info = store.xpath('./div[@class="store-map"]//script/text()').extract()
      geo_list = geo_info[0].split('var myLatLng = {')
      geo_info_s = geo_list[1]
      geo_list = geo_info_s.split('};')
      geo_info_s = geo_list[0].strip()
      geo_list = geo_info_s.split(',')
      lat = geo_list[0].strip().replace('lat: ', '')
      lng = geo_list[1].strip().replace('lng: ', '')
      
      item = ChainItem()
      item['store_name'] = store_name
      item['address'] = address
      item['city'] = city
      item['state'] = state
      item['zip_code'] = zip_code
      item['phone_number'] = phone
      item['store_hours'] = hour
      item['latitude'] = lat
      item['longitude'] = lng
      item['coming_soon'] = '0'
      item['country'] = 'United States'
      yield item
    else:
      print('++++++++++++++++++++++++++++++++++++++ no store detail')