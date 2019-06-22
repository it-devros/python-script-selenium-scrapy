# -*- coding: utf-8 -*-
import scrapy
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from OilFilters.items import OilfiltersItem
import time
import pdb


class Mobil2Spider(scrapy.Spider):
  name = 'mobil2'
  allowed_domain = 'https://mobiloil.com'
  start_url = 'https://mobiloil.com/en/product-selector'

  def __init__(self):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    self.driver = webdriver.Chrome("./chromedriver", options=options)
  
  def start_requests(self):
    url = self.allowed_domain
    yield scrapy.Request(url=url, callback=self.parse_search_page)
  
  def parse_search_page(self, response):
    url = self.start_url
    self.driver.get(url)

    is_year_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl00_DropDownListYear")))
    time.sleep(1)
    year_box = self.driver.find_element_by_id("maincontent_0_ctl00_DropDownListYear")
    yearList = [x.get_attribute("value") for x in year_box.find_elements_by_tag_name("option")]

    flag_year = 0
    flag_make = 0
    flag_model = 0

    for year in yearList:

      if year == "1985":
        flag_year = 1
      if year == "1984":
        flag_year = 0
      if year != "" and flag_year == 1:
        is_year_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl00_DropDownListYear")))
        time.sleep(1)
        self.driver.find_element_by_xpath('//select[@id="maincontent_0_ctl00_DropDownListYear"]/option[@value="' + year + '"]').click()

        try:
          is_make_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListMake")))
          time.sleep(1)
          make_box = self.driver.find_element_by_id("DropDownListMake")
          makeList = [x.get_attribute("value") for x in make_box.find_elements_by_tag_name("option")]

          for make in makeList:
            if make == "GMC":
              flag_make = 1
            if make != "" and flag_make == 1:
              is_make_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListMake")))
              time.sleep(1)
              self.driver.find_element_by_xpath('//select[@id="DropDownListMake"]/option[@value="' + make + '"]').click()

              try:
                is_model_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListModel")))
                time.sleep(1)
                model_box = self.driver.find_element_by_id("DropDownListModel")
                modelList = [x.get_attribute("value") for x in model_box.find_elements_by_tag_name("option")]

                for model in modelList:
                  if model == "C2500 Suburban":
                    flag_model = 1
                  if model != "" and flag_model == 1:
                    is_model_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListModel")))
                    time.sleep(1)
                    self.driver.find_element_by_xpath('//select[@id="DropDownListModel"]/option[@value="' + model + '"]').click()

                    try:
                      is_engine_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListEngine")))
                      time.sleep(1)
                      engine_box = self.driver.find_element_by_id("DropDownListEngine")
                      engineList = [x.get_attribute("value") for x in engine_box.find_elements_by_tag_name("option")]
                      types = []
                      filters = []
                      flag_success = 0

                      for engine in engineList:
                        if engine != "":

                          try:
                            is_engine_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListEngine")))
                            time.sleep(1)
                            self.driver.find_element_by_xpath('//select[@id="DropDownListEngine"]/option[@value="' + engine + '"]').click()
                            temperature_box = self.driver.find_element_by_xpath('//div[@class="form-group filter-nav-select temperature-question"]/select')
                            temperatureList = [x.get_attribute("value") for x in temperature_box.find_elements_by_tag_name("option")]
                            flag_index = 0

                            for temperature in temperatureList:
                              if temperature != "":

                                try:
                                  self.driver.find_element_by_xpath('//div[@class="form-group filter-nav-select temperature-question"]/select/option[@value="' + temperature + '"]').click()
                                except Exception as e:
                                  if flag_index == 0:
                                    print "no temperature status +++++++++++++++++++++++"
                                    self.driver.find_element_by_xpath('//div[@class="selector-form year-based"]//button').click()
                                    try:
                                      is_add_button_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl01_AddVehiclebuttonId")))
                                      time.sleep(1)
                                      types_filters_boxes = self.driver.find_elements_by_xpath('//header[@class="selector-header"]/h2/strong/a')
                                      for box in types_filters_boxes:
                                        val = box.get_attribute("data-placement")
                                        record = box.text.strip()
                                        if val == "bottom":
                                          if record not in types:
                                            types.append(record)
                                        else:
                                          if record not in filters:
                                            filters.append(record)
                                    except Exception as ex:
                                      print "no header here +++++++++++++++++ "
                                    self.driver.find_element_by_id("maincontent_0_ctl01_AddVehiclebuttonId").click()
                                    is_year_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl00_DropDownListYear")))
                                    time.sleep(1)
                                    self.driver.find_element_by_xpath('//select[@id="maincontent_0_ctl00_DropDownListYear"]/option[@value="' + year + '"]').click()
                                    is_make_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListMake")))
                                    time.sleep(1)
                                    self.driver.find_element_by_xpath('//select[@id="DropDownListMake"]/option[@value="' + make + '"]').click()
                                    is_model_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListModel")))
                                    time.sleep(1)
                                    self.driver.find_element_by_xpath('//select[@id="DropDownListModel"]/option[@value="' + model + '"]').click()
                                    is_engine_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListEngine")))
                                    time.sleep(1)
                                    self.driver.find_element_by_xpath('//select[@id="DropDownListEngine"]/option[@value="' + engine + '"]').click()
                                    flag_index = 1

                                if flag_index == 0:
                                  print "yes temperature status +++++++++++++++++++++++"
                                  self.driver.find_element_by_xpath('//div[@class="selector-form year-based"]//button').click()
                                  try:
                                    is_add_button_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl01_AddVehiclebuttonId")))
                                    time.sleep(1)
                                    types_filters_boxes = self.driver.find_elements_by_xpath('//header[@class="selector-header"]/h2/strong/a')
                                    for box in types_filters_boxes:
                                      val = box.get_attribute("data-placement")
                                      record = box.text.strip()
                                      if val == "bottom":
                                        if record not in types:
                                          types.append(record)
                                      else:
                                        if record not in filters:
                                          filters.append(record)
                                  except Exception as ex:
                                    print "no header here +++++++++++++++++ "

                                  self.driver.find_element_by_id("maincontent_0_ctl01_AddVehiclebuttonId").click()
                                  is_year_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "maincontent_0_ctl00_DropDownListYear")))
                                  time.sleep(1)
                                  self.driver.find_element_by_xpath('//select[@id="maincontent_0_ctl00_DropDownListYear"]/option[@value="' + year + '"]').click()
                                  is_make_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListMake")))
                                  time.sleep(1)
                                  self.driver.find_element_by_xpath('//select[@id="DropDownListMake"]/option[@value="' + make + '"]').click()
                                  is_model_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListModel")))
                                  time.sleep(1)
                                  self.driver.find_element_by_xpath('//select[@id="DropDownListModel"]/option[@value="' + model + '"]').click()
                                  is_engine_exist = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, "DropDownListEngine")))
                                  time.sleep(1)
                                  self.driver.find_element_by_xpath('//select[@id="DropDownListEngine"]/option[@value="' + engine + '"]').click()
                          except Exception as engineErr:
                            print "++++++++++ no such element error ++++++++++++++++"
                            pdb.set_trace()
      
                      if flag_success == 0:
                        item = OilfiltersItem()
                        item['year'] = year
                        item['make'] = make
                        item['model'] = model
                        item['types'] = types
                        item['filters'] = filters
                        yield item

                    except Exception as e_engine:
                      pdb.set_trace()

              except Exception as e_model:
                print "++++++++++++++ model box does not exist +++++++++++++"
                pdb.set_trace()

        except Exception as e_make:
          print "++++++++++++++ make box does not exist +++++++++++++"
          pdb.set_trace()



