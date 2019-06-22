import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class AlbertsonsSpider(scrapy.Spider):
  name = "albertsons"
  uid_list = []

  payload = '<request>\
      <appkey>C8EBB30E-9CDD-11E0-9770-6DB40E5AF53B</appkey>\
      <formdata id="locatorsearch">\
        <events>\
          <where>\
            <eventstartdate>\
              <ge>now()</ge>\
            </eventstartdate>\
          </where>\
          <limit>2</limit>\
        </events>\
        <dataview>store_default</dataview>\
        <geolocs>\
          <geoloc>\
            <addressline></addressline>\
            <longitude>&&long&&</longitude>\
            <latitude>&&lat&&</latitude>\
            <country>US</country>\
          </geoloc>\
        </geolocs>\
        <searchradius>15|25|50|100|250</searchradius>\
        <stateonly>1</stateonly>\
        <limit>20</limit>\
        <where>\
          <country>US</country>\
          <closed>\
            <distinctfrom>1</distinctfrom>\
          </closed>\
          <fuelparticipating>\
            <distinctfrom>1</distinctfrom>\
          </fuelparticipating>\
          <bakery><eq></eq></bakery>\
          <deli><eq></eq></deli>\
          <floral><eq></eq></floral>\
          <liquor><eq></eq></liquor>\
          <meat><eq></eq></meat>\
          <pharmacy><eq></eq></pharmacy>\
          <produce><eq></eq></produce>\
          <jamba><eq></eq></jamba>\
          <seafood><eq></eq></seafood>\
          <starbucks><eq></eq></starbucks>\
          <video><eq></eq></video>\
          <fuelstation><eq></eq></fuelstation>\
          <dvdplay_kiosk><eq></eq></dvdplay_kiosk>\
          <coinmaster><eq></eq></coinmaster>\
          <wifi><eq></eq></wifi>\
          <bank><eq></eq></bank>\
          <seattlesbestcoffee><eq></eq></seattlesbestcoffee>\
          <beveragestewards><eq></eq></beveragestewards>\
          <photo><eq></eq></photo>\
          <wu><eq></eq></wu>\
          <debi_lilly_design><eq></eq></debi_lilly_design>\
          <delivery><eq></eq></delivery>\
          <fresh_cut_produce><eq></eq></fresh_cut_produce>\
        </where>\
      </formdata>\
    </request>'

  def __init__(self):
    long_lat_fp = open('uscanplaces.csv', 'rb')
    self.long_lat_reader = csv.reader(long_lat_fp)
  
  def start_requests(self):
    index = 1
    for row in self.long_lat_reader:
      payload = self.payload.replace("&&long&&", row[1]).replace("&&lat&&", row[0])         
      yield scrapy.Request(url='http://locator.safeway.com/ajax?xml_request=%s' % payload, callback=self.parse_store)

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
      item['store_hours'] = ""
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


