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

class SweettomatoesSpider(scrapy.Spider):
  name = 'sweettomatoes'
  domain = 'http://sweettomatoes.com'
  request_url = 'http://sweettomatoes.com/find-us/'
  cities = []
  states = []
  us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.cities = json.load(f)
    self.driver = webdriver.Chrome("./chromedriver.exe")
  
  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_search)
  
  def parse_search(self, response):
    url = self.request_url
    self.driver.get(url)
    time.sleep(2)
    mile_input = self.driver.find_element_by_id('lpr-search-within')
    mile_input.send_keys('100')

    key_input = self.driver.find_element_by_id('lpr-search-address')
    key_input.send_keys('')
    key_input.send_keys('CA')
    self.driver.find_element_by_id('lpr-search-button').click()
    time.sleep(8)
    source = self.driver.page_source.encode("utf8")
    tree = etree.HTML(source)
    with open('log.html', 'a') as f:
      f.write(source)
      f.close()
    stores_list = []
    try:
      stores_list = tree.xpath('//div[@class="thumbnail alert-info"]')
      print('+++++++++++++++++++++++++++++')
      print(stores_list)
      if stores_list:
        for store_li in stores_list:
          latitude = store_li.xpath('.//div[@class="lpr-location"]/@data-lat')[0]
          longitude = store_li.xpath('.//div[@class="lpr-location"]/@data-lng')[0]
          print(latitude)
    except:
      print('++++++++++++++++++++++++++++++++++++++ no stores')
