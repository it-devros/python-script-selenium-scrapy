import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class JiffylubeSpider(scrapy.Spider):
  name = "jiffylube"
  request_url = "https://www.jiffylube.com/api/locations?lat=%s&lng=%s"
  uid_list = []

  def __init__(self):
    long_lat_fp = open('uscanplaces.csv', 'rb')
    self.long_lat_reader = csv.reader(long_lat_fp)
  
  def start_requests(self):
    for row in self.long_lat_reader:
      url = self.request_url % (row[0], row[1])
      yield scrapy.Request(url=url, callback=self.parse_store)

  # get longitude and latitude for a state by using google map.
  def parse_store(self, response):
    stores = json.loads(response.body)
    for store in stores:
      item = ChainItem()
      item['store_name'] = ""
      temp_store_services = self.validate(store, "service_groups")
      
      if temp_store_services:
        item['store_name'] = temp_store_services[0]["name"]

      item['store_number'] = self.validate(store,"id")
      item['address'] = self.validate(store, "address")
      item['address2'] = ""
      item['phone_number'] = self.validate(store, "phone_main")
      item['city'] = self.validate(store, "city")
      item['state'] = self.validate(store, "state")

      item['zip_code'] = self.validate(store, "postal_code")
      item['country'] = self.validate(store, "country")
      if store["coordinates"]:
        item['latitude'] = store["coordinates"]["latitude"]
        item['longitude'] = store["coordinates"]["longitude"]

      
      temp_store_hours = self.validate(store, "hours")
      hours_list = list(temp_store_hours)
      temp_hours = ''
      for hour_list in hours_list:
        hour_list.encode('ascii', 'replace')
        temp_hours += hour_list
        temp_hours += '; '

      temp_hours_u = temp_hours.decode('utf-8')
      item['store_hours'] = temp_hours_u
      #item['store_type'] = info_json["@type"]
      item['other_fields'] = ""
      item['coming_soon'] = "0"

      if item["store_number"] != "" and item["store_number"] in self.uid_list:
        return
 
      self.uid_list.append(item["store_number"])

      print item
      yield item

  # get store info in store detail page
  #def parse_store_content(self, response):
  #    pass

  def validate(self, store, property):
    try:
      return store[property]
    except:
      return ""



