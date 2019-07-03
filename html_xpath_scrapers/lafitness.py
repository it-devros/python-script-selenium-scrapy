import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class lafitnessSpider(scrapy.Spider):
  name = "lafitness"
  domain = "https://www.lafitness.com/Pages/"

  start_urls = ["https://www.lafitness.com/Pages/findclub.aspx",]
 
  # get all list of states
  def parse(self, response):
    states = response.xpath("//select[@name='ctl00$MainContent$FindAClub1$cboSelState']/option/text()").extract()
    for state in states:
      if state.strip() == "":
        continue
      yield scrapy.Request(url="%sfindclubresultszip.aspx?state=%s" % (self.domain, state), callback=self.parse_stores)

  # get list of stores
  def parse_stores(self, response):
    stores = response.xpath("//td[@class='TextDataColumn']/a/@href").extract()
    for store in stores:
      yield scrapy.Request(url=self.domain + store, callback=self.parse_store)

  # pare store detail page
  def parse_store(self, response):
    item = ChainItem()
    item['store_name'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblClubDescription']/text()"))
    item['store_number'] = response.url.split("clubid=")[1].split("&")[0]
    item['address'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblClubAddress']/text()"))
    item['phone_number'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblClubPhone']/text()"))
    item['city'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblClubCity']/text()"))
    item['state'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblClubState']/text()"))
    item['zip_code'] = self.validate(response.xpath("//span[@id='ctl00_MainContent_lblZipCode']/text()"))

    if item['state'] in ["AB", "ON"]:
      item['country'] = "Canada"
    else:
      item['country'] = "United States"

    item['latitude'] = ""
    item['longitude'] = ""
    item['store_hours'] = []
    temp = response.xpath("//div[@id='divClubHourPanel']//tr")

    for hr in temp[1:]:
      td = hr.xpath(".//td")
      item['store_hours'].append("%s: %s" % (self.validate(td[1].xpath("./b/text()")), \
           self.validate(td[2].xpath("./text()"))))

    item['store_hours'] = "; ".join(item['store_hours'])
    #item['store_type'] = info_json["@type"]
    item['other_fields'] = ""
    item['coming_soon'] = "0"
    yield item

  def validate(self, xpath_obj):
    try:
      return xpath_obj.extract_first().strip()
    except:
      return ""


