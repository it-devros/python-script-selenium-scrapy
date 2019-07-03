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

class OcharleysSpider(scrapy.Spider):
  name = 'ocharleys'
  request_url = 'http://www.ocharleys.com/api/Location/GetLocations?Latitude=%s&Longitude=%s&count=5'
  cities = []
  uid_list = []
  us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.cities = json.load(f)

  def start_requests(self):
    # for city in self.cities:
    #     if self.cities[city]['state'] in self.us_state_list:
    #         url = self.request_url % (self.cities[city]['latitude'], self.cities[city]['longitude'])
    #         yield scrapy.Request(url=url, callback=self.parse_store)
    url = 'http://www.ocharleys.com/api/Location/GetLocations?Latitude=40.7127837&Longitude=-74.00594130000002&count=1000'
    yield scrapy.Request(url=url, callback=self.parse_store)
  
  def parse_store(self, response):
    stores = json.loads(response.body)

    if stores:
      for store in stores:
        temp_store_number = store['StoreId']
        if not temp_store_number in self.uid_list:
          self.uid_list.append(temp_store_number)
          item = ChainItem()
          item['store_number'] = temp_store_number
          item['store_name'] = store['Name']
          item['address'] = store['Address']
          item['city'] = store['City']
          item['state'] = store['State']
          item['zip_code'] = store['Zip']
          item['country'] = 'United States'
          item['phone_number'] = store['MainPhone']
          item['latitude'] = store['Latitude']
          item['longitude'] = store['Longitude']
          temp_hour = ''
          temp_hour += 'Mon ' + store['MonOpen'] + ' - ' + store['MonClose'] + '; '
          temp_hour += 'Tue ' + store['TueOpen'] + ' - ' + store['TueClose'] + '; '
          temp_hour += 'Wed ' + store['WedOpen'] + ' - ' + store['WedClose'] + '; '
          temp_hour += 'Thu ' + store['ThuOpen'] + ' - ' + store['ThuClose'] + '; '
          temp_hour += 'Fri ' + store['FriOpen'] + ' - ' + store['FriClose'] + '; '
          temp_hour += 'Sat ' + store['SatOpen'] + ' - ' + store['SatClose'] + '; '
          temp_hour += 'Sun ' + store['SunOpen'] + ' - ' + store['SunClose'] + '; '
          item['store_hours'] = temp_hour
          yield item
        else:
          print('+++++++++++++++++++++++++++++ already scraped')
    else:
      print('++++++++++++++++ there are not stores')

  