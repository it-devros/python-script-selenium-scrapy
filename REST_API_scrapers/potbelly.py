import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class PotbellySpider(scrapy.Spider):
  name = "potbelly"
 
  def __init__(self):
    long_lat_fp = open('uscanplaces.csv', 'rb')
    self.long_lat_reader = csv.reader(long_lat_fp)

    self.store_numbers = []
    self.headers = {"Accept": "*/*"}
 
  def start_requests(self):
    for row in self.long_lat_reader:         
      yield scrapy.Request(url='https://api-origin.potbelly.com/proxy/v15/apps/1055/locations?lat=%s&lng=%s&fulfillment_types=pickup&in_delivery_area=false&has_breakfast=false'
             % (row[0], row[1]), callback=self.parse_store, headers = self.headers)

  def parse_store(self, response):
    stores = json.loads(response.body)

    for store in stores:
      store = store["location"]
      if store["id"] in self.store_numbers:
        continue

      self.store_numbers.append(store["id"])

      item = ChainItem()
      item['store_name'] = store["name"]
      item['store_number'] = store["id"]
      item['address'] = store["street_address"]
      item['address2'] = store["extended_address"]

      item['phone_number'] = store["phone"]
      item['latitude'] = store["latitude"]
      item['longitude'] = store["longitude"]
      item['city'] = store["locality"]
      item['state'] = store["region"]
      item['zip_code'] = store["postal_code"]
      try:
        temp = int(item['zip_code'])
        item['country'] = "United States"
      except:
        item['country'] = "Canada"

      item['store_hours'] = "; ".join(store["hours"].split("\r\n"))

      #item['store_type'] = info_json["@type"]
      item['other_fields'] = ""
      item['coming_soon'] = "0"
      yield item
  



