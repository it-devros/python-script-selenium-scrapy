import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class SamsclubSpider(scrapy.Spider):
  name = "samsclub"
  search_url = "http://www3.samsclub.com/clublocator/statelisting.aspx?mySearch=state&myState="

  start_urls = ["http://www3.samsclub.com/clublocator/",]
 
  def parse(self, response):
    states = response.xpath("//select[@id='ctl00_MainContent_ddlState']/option/text()").extract()
    for state in states:
      if state.strip() == "":
        continue
      yield scrapy.Request(url=self.search_url+state, callback=self.parse_stores)

  def parse_stores(self, response):
    body = response.body
    try:
      json_str = body.split(";plotClubs(")[1].split(",true, null")[0].strip()
      json_str = '[{"Address1"' + json_str.split(',[{"Address1"')[1]
    except:
      return

    stores = json.loads(json_str)
    for store in stores:
      item = ChainItem()
      item['store_name'] = store["ClubName"]
      item['store_number'] = store["ClubNumber"]
      item['address'] = store["Address1"]
      item['address2'] = store["Address2"] if store["Address2"] != None else ""
      item['phone_number'] = store["PhoneNumber"]
      item['city'] = store["City"]
      item['state'] = store["State"]
      item['zip_code'] = store["PostalCode"]
      item['country'] = "United States"
      item['latitude'] = store["Latitude"]
      item['longitude'] = store["Longitude"]
      item['store_hours'] = []
      for hr in store["Schedule"]:
        item['store_hours'].append("%s: %s" % (hr["Type"], hr["Summary"].replace("\n", "; ")))
      item['store_hours'] = "; ".join(item['store_hours']).strip()

      #item['store_type'] = info_json["@type"]
      item['other_fields'] = ""
      item['coming_soon'] = "0"
      yield item



