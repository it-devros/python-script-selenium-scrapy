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


class ColdstonecreamerySpider(scrapy.Spider):
  name = "coldstonecreamery"
  request_url = "https://www.coldstonecreamery.com/locator/index.php?brand=csc&mode=desktop&pagesize=200&mi_or_km=mi&q=%s&latitude=%s&longitude=%s"
  domain = 'https://www.coldstonecreamery.com'
  states = []
  uid_list = []

  def __init__(self):
    with open('states.json', 'r') as f:
      self.states = json.load(f)
  
  def start_requests(self):
    for state in self.states:
      url = self.request_url % (state['code'], state['latitude'], state['longitude'])
      yield scrapy.Request(url=url, callback=self.parse_store)

  def parse_store(self, response):
    script_list = response.xpath('//script/text()').extract()
    for script_li in script_list:
      temp_str = 'Locator.stores'
      if temp_str in script_li:
        json_string_list = script_li.split(' = ')
        json_string_temp = json_string_list[1].split('Locator')
        json_string = json_string_temp[0][:-4]
        store_data = json.loads(json_string)
        store_id = store_data['StoreId']
        if not store_id in self.uid_list:
          self.uid_list.append(store_id)
          item = ChainItem()
          item['store_number'] = store_data['StoreId']
          item['store_name'] = 'Cold Stone Creamery'
          item['address'] = store_data['Address'][:-2]
          item['city'] = store_data['City']
          item['state'] = store_data['State']
          item['zip_code'] = store_data['Zip']
          item['latitude'] = store_data['Latitude']
          item['longitude'] = store_data['Longitude']
          item['phone_number'] = store_data['Phone']
          item['address2'] = store_data['LocationHelp']
          item['country'] = store_data['CountryName']
          sum_hours = ''
          for hour in store_data['StoreHours']:
            sum_hours += hour['Hour'] + '; '
          item['store_hours'] = sum_hours

          yield item
        else:
          print("++++++++++++++++ already scraped")

    