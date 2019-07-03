import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem


class FredericmalleSpider(scrapy.Spider):
  name = "fredericmalle"
  start_urls = ['https://www.fredericmalle.com/eu/stores']
  main_location = [["Paris", "France"], ["London", "England"], ["Rome", "Italy"], ["New York", "United States"]]

  # get store info in store detail page
  def parse(self, response):
    # get main stores
    for index in range(0, 4):
      store_block = response.xpath("//div[contains(@class, 'store-list-%d')]" % index)
      addresses = store_block.xpath(".//div[@class='adresse']")
      open_hours = store_block.xpath(".//div[@class='horaire']")

      for store_idx in range(0, len(addresses)):
        item = self.get_init_store()
        address = addresses[store_idx].xpath("./text()").extract()

        item["city"] = self.main_location[index][0]
        item["country"] = self.main_location[index][1]
        item["address"] = address[0].strip()
        if item["city"] == "New York":
          item["zip_code"] = " ".join(address[1].split(" ")[:2]).strip()
        else:
          item["zip_code"] = " ".join(address[1].split(" ")[:-1]).strip()

        item["phone_number"] = address[2].split(":")[1].strip()
        tp_ophr = open_hours[store_idx].xpath("./text()").extract()

        try:
          item["store_hours"] = "; ".join([tp.strip() for tp in tp_ophr])
          yield item
        except:
          print item

    # get other stores
    countries = response.xpath("//div[contains(@class, 'store-country-2')]/text()").extract()
    store_blocks = response.xpath("//div[contains(@class, 'country-adress')]")
    for st_index in range(0, len(countries)):
      if countries[st_index] not in ["United States", "Canada"]:
        continue

      city = ""
      store_block = store_blocks[st_index].xpath(".//div[contains(@class, 'country-container')]")
      for store in store_block:
        item = self.get_init_store()

        temp = store.xpath(".//div[contains(@class, 'title')]/text()").extract_first().strip()
        if temp != "":
          city = temp
        address = store.xpath(".//div[@class='adresse']/text()").extract()

        # get store name
        index = 0
        value = address[0]

        if True: #try:
          while self.check_upper(value):
            item["store_name"] += " " + value.replace("\r\n", "").strip()
            index += 1
            value = address[index]
        #except:
        #    pass
        item["store_name"] = item["store_name"].strip()

        tp_index = index
        # get address
        try:
          while value.replace("\r\n", "").lower().find(city.lower()) == -1 or value.split(" ")[-1].isdigit() == False:
            item["address"] += " " + value.replace("\r\n", "").strip()
            index += 1
            value = address[index]
        except:
          index = tp_index
          value = address[index]
          item["address"] += " " + value.replace("\r\n", "").strip()

        item["address"] = item["address"].strip()

        item['zip_code'] = value.replace("\r\n", "").replace(",", "").lower().replace(city.lower(), "").strip().upper()

        # get phone number
        try:
          while value.find(":") == -1:
            index += 1
            value = address[index]
          item['phone_number'] = address[index].replace("\r\n", "").split(":")[1].strip()
        except:
          pass

        item["country"] = countries[st_index].strip()
        item["city"] = city
        yield item

  def get_init_store(self):
    item = ChainItem()
    item['store_name'] = ""
    item['store_number'] = ""
    item['address'] = ""
    item['phone_number'] = ""
    item['city'] = ""
    item['state'] = ""
    item['zip_code'] = ""
    item['country'] = ""
    item['latitude'] = ""
    item['longitude'] = ""
    item['store_hours'] = ""
    #item['store_type'] = info_json["@type"]
    item['other_fields'] = ""
    item['coming_soon'] = "0"
    return item

  def check_upper(self, value):
    value = value.replace("\r\n", "").strip()
    return all(char.isupper() for char in value if char != " ")


