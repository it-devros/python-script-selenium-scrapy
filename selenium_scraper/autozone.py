# -*- coding: utf-8 -*-
import scrapy
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from OilFilters.items import OilfiltersItem
import pdb


class AutozoneSpider(scrapy.Spider):
  name = 'autozone'
  allowed_domain = 'https://www.autozone.com'
  start_url = 'https://www.autozone.com/ignition-tune-up-and-routine-maintenance/oil-filter'

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver")

  def start_requests(self):
    url = "https://mobiloil.com"
    yield scrapy.Request(url=url, callback=self.parse_search_page)

  def parse_search_page(self, response):
    url = self.start_url
    self.driver.get(url=url)
    time.sleep(5)
    try:
      is_year_exist = WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.NAME, "year")))
      year_box = self.driver.find_element_by_name("year")
      yearList = [{ 'value': x.get_attribute("value"), 'text': x.text } for x in year_box.find_elements_by_tag_name("option")]
      flag_year = 0
      flag_make = 0
      flag_model = 0

      for year in yearList:
        if year['text'] == "2019":
          flag_year = 1
        if year['text'] == "2015":
          flag_year = 0

        if year['text'] != "Year" and flag_year == 1:
          self.driver.find_element_by_xpath("//select[@name='year']/option[@value='" + year['value'].strip() + "']").click()
          time.sleep(2)
          make_box = self.driver.find_element_by_name("make")
          makeList = [{ 'value': x.get_attribute("value"), 'text': x.text } for x in make_box.find_elements_by_tag_name("option")]

          for make in makeList:
            if make['text'] == "International":
              flag_make = 1

            if make['text'] != "Make" and flag_make == 1:
              self.driver.find_element_by_xpath("//select[@name='make']/option[@value='" + make['value'].strip() + "']").click()
              time.sleep(2)
              model_box = self.driver.find_element_by_name("model")
              modelList = [{ 'value': x.get_attribute("value"), 'text': x.text } for x in model_box.find_elements_by_tag_name("option")]

              for model in modelList:
                if model['text'] == "7500":
                  flag_model = 1
                  
                if model['text'] != "Model" and flag_model == 1:
                  self.driver.find_element_by_xpath("//select[@name='model']/option[@value='" + model['value'].strip() + "']").click()
                  time.sleep(2)
                  engine_box = self.driver.find_element_by_name("engine")
                  engineList = [{ 'value': x.get_attribute("value"), 'text': x.text } for x in engine_box.find_elements_by_tag_name("option")]
                  types = []
                  filters = []
                  for engine in engineList:
                    if engine['text'] != "Engine":
                      self.driver.find_element_by_xpath("//select[@name='engine']/option[@value='" + engine['value'].strip() + "']").click()
                      time.sleep(1)
                      self.driver.find_element_by_xpath("//form[@name='ymme-form']/button").click()
                      time.sleep(5)
                      try:
                        is_remove_exist = WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.ID, "ymme-header")))
                        item_boxes = self.driver.find_elements_by_xpath("//div[@id='shelfItems']/div[@typeof='Product']")
                        if len(item_boxes) > 0:
                          for item_box in item_boxes:
                            name = item_box.find_element_by_xpath(".//span[@property='name']").text.strip()
                            part_number = item_box.find_element_by_xpath(".//span[@property='mpn']").text.strip()
                            temp_array = []
                            temp_array.append(name)
                            temp_array.append(part_number)
                            filters.append(temp_array)

                        self.driver.find_element_by_xpath("//div[@id='mainContent']//div[@id='ymme-header']/a[@class='allProducts']").click()
                        time.sleep(5)
                        try:
                          is_year_exist_1 = WebDriverWait(self.driver, 600).until(EC.presence_of_element_located((By.NAME, "year")))
                          self.driver.find_element_by_xpath("//select[@name='year']/option[@value='" + year['value'].strip() + "']").click()
                          time.sleep(2)
                          self.driver.find_element_by_xpath("//select[@name='make']/option[@value='" + make['value'].strip() + "']").click()
                          time.sleep(2)
                          self.driver.find_element_by_xpath("//select[@name='model']/option[@value='" + model['value'].strip() + "']").click()
                          time.sleep(2)
                        except:
                          print "++++++++++++++++ captcha detected for search page again ++++++++++++++"
                      except:
                        print "++++++++++++++++ captcha detected for result page ++++++++++++++"
                  item = OilfiltersItem()
                  item['year'] = year['text']
                  item['make'] = make['text']
                  item['model'] = model['text']
                  item['types'] = types
                  item['filters'] = filters
                  yield item
    except:
      print "++++++++++++++++ captcha detected for search page ++++++++++++++"

                
                
