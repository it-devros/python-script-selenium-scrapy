import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class EastsidemariosSpider(scrapy.Spider):
  name = 'eastsidemarios'
  domain = 'http://www.eastsidemarios.com'
  start_url = 'http://www.eastsidemarios.com/locations/'
  stores = []
  def start_requests(self):
    url = self.start_url
    yield scrapy.Request(url=url, callback=self.parse_stores)
  
  def parse_stores(self, response):
    script_locations = response.xpath('//script[@type="text/javascript"]/text()').extract()
    if script_locations:
      for script_li in script_locations:
        if script_li.find('var allLocations = ') == 0:
          script_li = script_li.replace('var allLocations = ', '')
          self.stores = json.loads(script_li)
        else:
          print('++++++++++++++++++++++++++++++ no stores')

      for store in self.stores:
        url = store['url']
        request = scrapy.Request(url=url, callback=self.parse_detail)
        request.meta['id'] = store['id']
        request.meta['title'] = store['title']
        request.meta['address'] = store['address']
        request.meta['phone'] = store['phone']
        request.meta['lat'] = store['lat']
        request.meta['lng'] = store['lng']
        yield request
    else:
      print('++++++++++++++++++++++++++++++++++++++++++ no scripts')
  
  def parse_detail(self, response):
    p_lists = response.xpath('//div[@class="col-md-6"]//p')
    i = 0
    hours = ''
    try:
      temp_list = p_lists[2].xpath('./text()').extract()
      for temp in temp_list:     
        hours += temp + '; '
    except:
      print('++++++++++++++++++++++++++++++++++++++++ no store hours')
      hours = ''
    
    item = ChainItem()
    item['store_name'] = response.meta['title']
    item['store_number'] = response.meta['id']
    if response.meta['phone'] != 'Coming Soon!':
      item['phone_number'] = response.meta['phone']
      item['coming_soon'] = '0'
    else:
      item['coming_soon'] = '1'
    item['latitude'] = response.meta['lat']
    item['longitude'] = response.meta['lng']
    item['store_hours'] = hours
    address = response.meta['address']
    addr_list = address.split('<br />')
    item['address'] = addr_list[0]
    address = addr_list[1]
    addr_list = address.split(', ')
    item['city'] = addr_list[0].encode('raw-unicode-escape').replace('\xc3', '')
    address = addr_list[1]
    addr_list = address.split(' ')
    item['state'] = addr_list[0]
    try:
      item['zip_code'] = addr_list[1] + ' ' + addr_list[2]
      if addr_list[3]:
        item['state'] += addr_list[1]
        item['zip_code'] = addr_list[2] + ' ' + addr_list[3]
    except:
      print('ok')
      
    
    yield item
    