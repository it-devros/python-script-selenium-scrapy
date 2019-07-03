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
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

class ShoeshowSpider(scrapy.Spider):
  name = "shoeshow"
  request_url = "https://www.shoeshow.com/find-a-store"
  domain ='https://www.shoeshow.com/'
  us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
  canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
  zip_lines = []
  uid_list = []

  def __init__(self):
    with open('citiesusca.json', 'r') as f:
      self.zip_lines = json.load(f)
    self.driver = webdriver.Chrome("./chromedriver.exe")
    
  
  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_state)

  def parse_state(self, response):
    url = self.request_url
    
    for zip_line in self.zip_lines:
      self.driver.get(url)
      time.sleep(1)
      line = self.zip_lines[zip_line]['zip_code']
      zip_input = self.driver.find_element_by_name("txtZipCode")
      zip_input.send_keys('')
      zip_input.send_keys(line)
      self.driver.find_element_by_id("lnkFindStore").click()
      time.sleep(1)
      source = self.driver.page_source.encode("utf8")
      tree = etree.HTML(source)
      store_list = []
      try:
        store_list = tree.xpath('//ol[@class="find-store-list"]//li')
      except:
        print("++++++++++++++++++++++++++ no stores in this zip code")

      if store_list:
        for store_li in store_list:
          store_info = self.validate(store_li.xpath('./text()'))
          if store_info:
            temp_number = self.validate(store_li.xpath('.//strong/text()'))
            if not temp_number[0] in self.uid_list:
              self.uid_list.append(temp_number[0])
              item = ChainItem()
              item['store_number'] = self.string_validate(temp_number[0])
              item['store_name'] = self.string_validate(store_info[0].strip())
              item['address'] = self.string_validate(store_info[1].strip())
              flag_d = 0
              try:
                temp_str = self.string_validate(store_info[2].strip())
                temp_k = 'AM'
                if temp_k in temp_str:
                  temp_str = self.string_validate(store_info[1].strip())
                  flag_d = 1
                temp_str_city = self.validate(temp_str.split(', '))
                item['city'] = self.string_validate(temp_str_city[0].strip())
                temp_str = self.string_validate(temp_str_city[1].strip())
                temp_str_city = self.validate(temp_str.split(' '))
                item['state'] = self.string_validate(temp_str_city[0].strip())
                item['zip_code'] = self.string_validate(temp_str_city[1].strip())
              except:
                item['city'] = 'None'
                item['state'] = 'None'
                item['zip_code'] = 'None'

              temp_number_phone = self.validate(store_li.xpath('.//a/text()'))
              item['phone_number'] = self.string_validate(temp_number_phone[0])
              try:
                if flag_d == 1:
                  temp_hour_work = self.string_validate(store_info[2].strip())
                  temp_hour_relax = self.string_validate(store_info[3].strip())
                  item['store_hours'] = temp_hour_work + '; ' + temp_hour_relax
                else:
                  temp_hour_work = self.string_validate(store_info[3].strip())
                  temp_hour_relax = self.string_validate(store_info[4].strip())
                  item['store_hours'] = temp_hour_work + '; ' + temp_hour_relax
              except:
                item['store_hours'] = 'None'

              if item['state'] in self.us_state_list:
                item['country'] = 'United States'
              if item['state'] in self.canada_state_list:
                item['country'] = 'Canada'
              
              yield item

            else:
              print("++++++++++++++++++++++++++++ already scraped")
          else:
            print("++++++++++++++++++++++++++++++++ there is not li")



  def validate(self, some_list):
    try:
      if some_list:
        return some_list
    except:
      print("++++++++++++++++++++++++++++++++++value error. I can't get the DOM")
      temp_list = ['None', 'None']
      return temp_list

  def string_validate(self, some_string):
    try:
      if some_string:
        return some_string
    except:
      print("++++++++++++++++++++++++++++++++++ string is empty")
      temp_string = 'None'
      return temp_string
  