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

class AaronSpider(scrapy.Spider):
  name = "aaron"
  request_url = "https://www.aarons.com/storelocator.aspx"
  state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
  us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
  canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
  uid_list = []
  domain ='https://www.aarons.com/'

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver.exe")

  
  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_state)

  def parse_state(self, response):
    url = self.request_url
    self.driver.get(url)
    self.driver.find_element_by_id("locationFinderPupUpHeaderRespCloseLbl").click()
    time.sleep(3)
    tt = 0
    for state_url in self.state_list:
      # self.driver.get(url)
      # time.sleep(3)
      # state = self.driver.find_element_by_id("ctl00_PageContent_SelectState")
      # state.send_keys(state_url)
      # self.driver.find_element_by_id("ctl00_PageContent_btnStoreSearch").click()

      send_url = url + '?s=' + state_url
      self.driver.get(send_url)
      time.sleep(3)
      source = self.driver.page_source.encode("utf8")
      tree = etree.HTML(source)
      total_count = 0
      number_pagination_temp = []
      try:
        number_pagination_temp = tree.xpath('//span[@id="ctl00_PageContent_lblPageInfo"]')
        print(number_pagination_temp[0].xpath('./text()'))
        number_pagination = number_pagination_temp[0].xpath('./text()')[0]
        print(number_pagination)
        number = number_pagination[-1:]
        print(number)
        total_count = int(number)
        print(total_count)
      except:
        total_count = 0
        print("+++++++++++++++++++++++++++++++++++ pagination does not exist.")

      if total_count > 0:
        i = 0
        
        while (i < total_count):
          stores_list = []
          try:
            stores_list = tree.xpath('//a[@class="StoreLocLink"]')
          except:
            stores_list = []
            print("++++++++++++++++++++++++++++++++++ stores does not exist.")

          for store in stores_list:
            
            temp_str = store.xpath('./text()')[0]
            temp_str_name = temp_str.strip()
            temp_str_list = temp_str_name.split('(')
            temp_store_name = temp_str_list[0].strip()
            temp_store_number = temp_str_list[1][:-1]
            
            if not temp_store_number in self.uid_list:
              self.uid_list.append(temp_store_number)
              
              detail_url = self.domain + store.xpath('./@href')[0]
              self.driver.get(detail_url)
              time.sleep(3)
              # btn_detail = self.driver.find_element_by_xpath('//a[@href="'+detail_url+'"]').click()
              source_detail = self.driver.page_source.encode("utf8")
              tree_detail = etree.HTML(source_detail)
              try:
                item = ChainItem()
                item['store_number'] = temp_store_number
                item['store_name'] = temp_store_name
                temp_str_state = self.validate(tree_detail.xpath('//span[@itemprop="region"]/text()'))
                item['state'] = temp_str_state[0]
                temp_str_addr = self.validate(tree_detail.xpath('//span[@itemprop="street-address"]/text()'))
                temp_str_locality = self.validate(tree_detail.xpath('//span[@itemprop="locality"]/text()'))
                temp_str = temp_str_addr[0] + ' ' + temp_str_locality[0]
                item['address'] = temp_str
                item['city'] = temp_str_locality
                temp_str_zip = self.validate(tree_detail.xpath('//span[@itemprop="postal-code"]/text()'))
                item['zip_code'] = temp_str_zip[0].strip()
                if item['state'] in self.us_state_list:
                  item['country'] = 'United States'
                if item['state'] in self.canada_state_list:
                  item['country'] = 'Canada'
                temp_str_tel = self.validate(tree_detail.xpath('//span[@itemprop="tel"]/text()'))
                item['phone_number'] = temp_str_tel[0]
                temp = ''
                temp_hour_list = self.validate(tree_detail.xpath('//div[@class="weekdaystable"]//div'))
                for temp_hour in temp_hour_list:
                  temp_hour_name = self.validate(temp_hour.xpath('.//span[@class="dayname"]/text()'))
                  temp_hour_contents = temp_hour.xpath('./text()')
                  temp_hour_content = ''
                  for temp_time in temp_hour_contents:
                    temp_hour_content += temp_time
                  temp += temp_hour_name[0] + ' ' + temp_hour_content + '; '
                item['store_hours'] = temp 
                yield item
              except:
                tt = 0
                print("+++++++++++++++++++++++++++++Page is permanatly deleted")
            else:
              print("++++++++++++++++++++++++++++++++ aready scraped")    
          try:
            self.driver.get(self.request_url + '?s=' + state_url)
            k = 0
            i = i + 1
            while (k < i):
              self.driver.find_element_by_id("ctl00_PageContent_lbtnNext").click()
              time.sleep(3)
              k = k + 1
          except:
            tt = 0
            print("+++++++++++++++++++++++++++pagination next button not recognized.")
          
          source = self.driver.page_source.encode("utf8")
          tree = etree.HTML(source)
      else:
        stores_list = []
        try:
          stores_list = tree.xpath('//a[@class="StoreLocLink"]')
        except:
          stores_list = []
          print("++++++++++++++++++++++++++++++++++ stores does not exist.")

        if stores_list:

          for store in stores_list:
            
            temp_str = store.xpath('./text()')[0]
            temp_str_name = temp_str.strip()
            temp_str_list = temp_str_name.split('(')
            temp_store_name = temp_str_list[0].strip()
            temp_store_number = temp_str_list[1][:-1]
            
            if not temp_store_number in self.uid_list:
              self.uid_list.append(temp_store_number)
              
              detail_url = self.domain + store.xpath('./@href')[0]
              self.driver.get(detail_url)
              time.sleep(3)
              # btn_detail = self.driver.find_element_by_xpath('//a[@href="'+detail_url+'"]').click()
              source_detail = self.driver.page_source.encode("utf8")
              tree_detail = etree.HTML(source_detail)
              try:
                item = ChainItem()
                item['store_number'] = temp_store_number
                item['store_name'] = temp_store_name
                temp_str_state = self.validate(tree_detail.xpath('//span[@itemprop="region"]/text()'))
                item['state'] = temp_str_state[0]
                temp_str_addr = self.validate(tree_detail.xpath('//span[@itemprop="street-address"]/text()'))
                temp_str_locality = self.validate(tree_detail.xpath('//span[@itemprop="locality"]/text()'))
                temp_str = temp_str_addr[0] + ' ' + temp_str_locality[0]
                item['address'] = temp_str
                item['city'] = temp_str_locality
                temp_str_zip = self.validate(tree_detail.xpath('//span[@itemprop="postal-code"]/text()'))
                item['zip_code'] = temp_str_zip[0].strip()
                if item['state'] in self.us_state_list:
                  item['country'] = 'United States'
                if item['state'] in self.canada_state_list:
                  item['country'] = 'Canada'
                temp_str_tel = self.validate(tree_detail.xpath('//span[@itemprop="tel"]/text()'))
                item['phone_number'] = temp_str_tel[0]
                temp = ''
                temp_hour_list = self.validate(tree_detail.xpath('//div[@class="weekdaystable"]//div'))
                for temp_hour in temp_hour_list:
                  temp_hour_name = self.validate(temp_hour.xpath('.//span[@class="dayname"]/text()'))
                  temp_hour_contents = temp_hour.xpath('./text()')
                  temp_hour_content = ''
                  for temp_time in temp_hour_contents:
                    temp_hour_content += temp_time
                  temp += temp_hour_name[0] + ' ' + temp_hour_content + '; '
                item['store_hours'] = temp 
                yield item
              except:
                tt = 0
                print("+++++++++++++++++++++++++++++Page is permanatly deleted")
            else:
              print("+++++++++++++++++++++++++++++++++ aready scraped")    
    self.driver.close()


  def validate(self, some_list):
    try:
      return some_list
    except:
      print("++++++++++++++++++++++++++++++++++value error. I can't get the DOM")
      temp_list = ['None', 'None']
      return temp_list





    

