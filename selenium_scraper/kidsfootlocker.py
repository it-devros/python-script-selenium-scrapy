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

class KidsfootlockerSpider(scrapy.Spider):
  name = 'kidsfootlocker'
  domain = 'http://www.kidsfootlocker.com'
  request_url = 'http://www.kidsfootlocker.com/storelocator#d=New York'
  cities = []
  countries = ['DE', 'ES', 'FR', 'GB', 'IT', 'NL,NE']

  def __init__(self):
    with open('citiesusca.json', 'rb') as f:
      self.states = json.load(f)
    self.driver = webdriver.Chrome("./chromedriver.exe")
  
  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_store)
  
  def parse_store(self, response):
    
    url = self.request_url
    print(url)
    self.driver.get(url)
    time.sleep(2)
    key_input = self.driver.find_element_by_name('address')
    key_input.send_keys('')
    key_input.send_keys('Los Angeles')
    self.driver.find_element_by_xpath('//form[@id="domestic_form"]//p//input[@value="Search"]').click()
    time.sleep(2)

    source = self.driver.page_source.encode("utf8")
    tree = etree.HTML(source)

    stores = tree.xpath('//ul[@id="stores"]//li[@class="location"]')
    if stores:
      i = 0
      for store in stores:
        i += 1
      print(i)

