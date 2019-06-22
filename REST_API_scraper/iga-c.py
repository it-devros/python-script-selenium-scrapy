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

class IgacSpider(scrapy.Spider):
  name = 'iga-c'
  request_url = 'https://www.iga.net/api/en/Store/get?Latitude=%s&Longitude=%s&Skip=0&Max=10'
  cities = []
  uid_list = []
  canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.cities = json.load(f)

  def start_requests(self):
    for city in self.cities:
      if self.cities[city]['state'] in self.canada_state_list:
        url = self.request_url % (self.cities[city]['latitude'], self.cities[city]['longitude'])
        request = scrapy.Request(url=url, callback=self.parse_store)
        request.meta['state_mine'] = self.cities[city]['state']
        yield request

  def parse_store(self, response):
    stores = json.loads(response.body)
    stores_list = []
    try:
      stores_list = stores['Data']
    except:
      print("+++++++++++++++++++++ no store lists")
      
    temp_state = response.meta['state_mine']
    if stores_list:
      for store in stores_list:
        temp_store_number = store['Number']
        if not temp_store_number in self.uid_list:
          self.uid_list.append(temp_store_number)
          item = ChainItem()
          item['store_name'] = store['Name']
          item['store_number'] = temp_store_number
          item['address'] = store['AddressMain']['Line']
          item['city'] = store['AddressMain']['City']
          item['state'] = temp_state
          item['zip_code'] = store['AddressMain']['PostalCode']
          item['country'] = 'Canada'
          item['phone_number'] = store['PhoneNumberHome']['Number']
          item['latitude'] = store['Coordinates']['Latitude']
          item['longitude'] = store['Coordinates']['Longitude']
          item['store_hours'] = store['OpeningHours']

          yield item
        else:
          print('+++++++++++++++++++++++++++++ already scraped')
    else:
      print('+++++++++++++++++++++++++ there are no any stores')
