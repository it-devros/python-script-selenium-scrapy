import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

from geopy.geocoders import Nominatim

class StarbucksSpider(scrapy.Spider):
  name = "starbucks"
 
  def __init__(self):
    long_lat_fp = open('uscanplaces.csv', 'rb')
    self.long_lat_reader = csv.reader(long_lat_fp)

    self.store_numbers = []
    self.geolocator = Nominatim()
 
  def start_requests(self):
    for row in self.long_lat_reader:         
      yield scrapy.Request(url='https://www.starbucks.ca/bff/locations?lat=%s&lng=%s'
             % (row[0], row[1]), callback=self.parse_store)

  def parse_store(self, response):
    stores = json.loads(response.body)["stores"]

    for store in stores:
      if store["storeNumber"] in self.store_numbers:
        continue

      self.store_numbers.append(store["storeNumber"])

      item = ChainItem()
      item['store_name'] = store["name"]
      item['store_number'] = store["storeNumber"]
      item['address'] = store["addressLines"][0]
      try:
        item['address2'] = store["addressLines"][1]
      except:
        pass

      item['phone_number'] = store["phoneNumber"] if "phoneNumber" in store else ""
      item['latitude'] = store["coordinates"]["latitude"]
      item['longitude'] = store["coordinates"]["longitude"]

      location = self.geolocator.reverse("%s, %s" % (str(item['latitude']), str(item['longitude'])))

      try:
        item['city'] = location.raw["address"]["city"]
      except:
        if 'town' in location.raw["address"]:
          item['city'] = location.raw["address"]["town"]

      item['state'] = location.raw["address"]["state"] if "state" in location.raw["address"] else ""
      item['zip_code'] = location.raw["address"]["postcode"]
      item['country'] = location.raw["address"]["country_code"].upper()

      item['store_hours'] = []

      try:
        for hr in store["schedule"]:
          item['store_hours'].append("%s: %s" % (hr["dayName"], hr["hours"]))
        item['store_hours'] = "; ".join(item['store_hours']).strip()
      except:
        item['store_hours'] = ""

      #item['store_type'] = info_json["@type"]
      item['other_fields'] = "Amenities"
      item['coming_soon'] = "0"
      yield item
  



