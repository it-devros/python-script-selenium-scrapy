import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class DollartreeSpider(scrapy.Spider):
  name = "dollartree"
  uid_list = []

  payload = '<request><appkey>134E9A7A-AB8F-11E3-80DE-744E58203F82</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>250</limit><geolocs><geoloc><addressline></addressline><longitude>$$$lg$$$</longitude><latitude>$$$lt$$$</latitude></geoloc></geolocs><searchradius>10|25|50|100|250</searchradius><where><icon><eq>DollarTree</eq></icon><ebt><eq></eq></ebt><freezers><eq></eq></freezers></where></formdata></request>'

  def __init__(self):
    long_lat_fp = open('uscanplaces.csv', 'rb')
    self.long_lat_reader = csv.reader(long_lat_fp)
  
  def start_requests(self):
    for row in self.long_lat_reader:
      payload = self.payload.replace("$$$lg$$$", row[1]).replace("$$$lt$$$", row[0])         
      yield scrapy.Request(url='https://hosted.where2getit.com/dollartree/ajax?xml_request=%s' % payload, callback=self.parse_store)
      return

  # get longitude and latitude for a state by using google map.
  def parse_store(self, response):
    stores = response.xpath("//poi")

    for store in stores:
      item = ChainItem()
      item['store_name'] = self.validate(store.xpath(".//name/text()"))
      item['store_number'] = self.validate(store.xpath(".//uid/text()"))
      item['address'] = self.validate(store.xpath(".//address1/text()"))
      item['address2'] = self.validate(store.xpath(".//address2/text()"))
      item['phone_number'] = self.validate(store.xpath(".//phone/text()"))
      item['city'] = self.validate(store.xpath(".//city/text()"))
      item['state'] = self.validate(store.xpath(".//province/text()"))
      if item['state'] == "":
        item['state'] = self.validate(store.xpath(".//state/text()"))

      item['zip_code'] = self.validate(store.xpath(".//postalcode/text()"))
      item['country'] = self.validate(store.xpath(".//country/text()"))
      item['latitude'] = self.validate(store.xpath(".//latitude/text()"))
      item['longitude'] = self.validate(store.xpath(".//longitude/text()"))
      item['store_hours'] = self.validate(store.xpath(".//hours/text()"))
      hour2 = self.validate(store.xpath(".//hours2/text()"))
      if hour2 != "":
        item['store_hours'] += "; " + hour2
         
      #item['store_type'] = info_json["@type"]
      item['other_fields'] = ""
      item['coming_soon'] = "0"

      if item["store_number"] != "" and item["store_number"] in self.uid_list:
        return
      self.uid_list.append(item["store_number"])
      yield item

  # get store info in store detail page
  #def parse_store_content(self, response):
  #    pass

  def validate(self, xpath_obj):
    try:
      return xpath_obj.extract_first().strip()
    except:
      return ""


