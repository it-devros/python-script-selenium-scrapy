import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import time

class dicap(scrapy.Spider):
  name = 'dicap'
  domain = 'http://www.medicap.com'
  history = []
  location_list = []

  def __init__(self):
    self.driver = webdriver.Chrome("./chromedriver")

  def start_requests(self):
    init_url = 'http://www.medicap.com/pharmacy-locations'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    init_url = 'http://www.medicap.com/pharmacy-locations'
    self.driver.get(init_url)
    time.sleep(2)
    source = self.driver.page_source.encode("utf8")
    tree = etree.HTML(source)
    links = tree.xpath('//ul[@class="state-search"]//li')
    for link in links:
      status = ''
      try:
        status = link.xpath('./@class')[0]
      except:
        pass
      if status != 'disabled':
        url_id = link.xpath('./a/@id')[0].strip()
        self.driver.find_element_by_id(url_id).click()
        time.sleep(1)
        source_body = self.driver.page_source.encode("utf8")
        tree_body = etree.HTML(source_body)
        store_list = tree_body.xpath('//ol[@class="brand-service-listing"]//li')
        for store in store_list:
          store_name = ''
          try:
            store_name = store.xpath('.//h3[@class="brand-name"]/a/text()')[0].strip()
          except:
            pass
          if store_name != '':
            item = ChainItem()
            item['store_name'] = store.xpath('.//h3[@class="brand-name"]/a/text()')[0].strip()
            detail_url = self.domain + store.xpath('.//h3[@class="brand-name"]/a/@href')[0].strip()
            self.driver.get(detail_url)
            time.sleep(1)
            source_detail = self.driver.page_source.encode("utf8")
            tree_detail = etree.HTML(source_detail)
            item['phone_number'] = tree_detail.xpath('//div[@class="contact-info"]//dl[@class="contact-details"]//dd/text()')[0].strip().replace('.', '-')
            item['address'] = tree_detail.xpath('//div[@class="scaddress"]/text()')[0].strip()
            sccityzip = self.validate(tree_detail.xpath('//div[@class="sccityzip"]/text()')[0])
            item['city'] = sccityzip.split(',')[0].strip()
            statezip = sccityzip.split(',')[1].strip()
            item['state'] = statezip.split(' ')[0].strip()
            item['zip_code'] = statezip.split('                    ')[1].strip()
            h_list = tree_detail.xpath('//div[@class="pharmacy-hours"]//ul//li')
            hours = ''
            i = 0
            count = len(h_list)
            for h in h_list:
              label = h.xpath('./div[@class="day"]/text()')[0].strip()
              hour = h.xpath('./div[@class="time"]/text()')[0].strip()
              if i < count - 1:
                hours += label + hour + ', '
              else:
                hours += label + hour
              i += 1
            if hours == '':
              h_list = tree_detail.xpath('//div[@class="pharmacy-hours"]//strong/text()')
              h_text = tree_detail.xpath('//div[@class="pharmacy-hours"]/text()')
              h_text_temp = ''
              if h_text:
                for h in h_text:
                  h_text_temp += h.strip()
              if not h_text or h_text_temp == '':
                i = 0
                count = len(h_list)
                for h in h_list:
                  if i < count - 1:
                    hours += h.strip() + ', '
                  else:
                    hours += h.strip()
                  i += 1
              else:
                i = 0
                count = len(h_list)
                comp_count = count - 1
                for h in h_list:
                  if i < comp_count:
                    if h_text[i].strip() == '':
                      i += 1
                      comp_count += 1
                    hours += h.strip() + h_text[i].strip() + ', '
                  else:
                    hours += h.strip() + h_text[i].strip()
                  i += 1
            if hours == '':
              h_list = tree_detail.xpath('//div[@class="pharmacy-hours"]/text()')
              i = 0
              count = len(h_list)
              for h in h_list:
                if i < count - 1:
                  hours += h.strip() + ', '
                else:
                  hours += h.strip()
              hours = hours.split(', We will')[0].strip()
            if hours.find(', , , , ,') != -1:
              hours = ''
              h_list = tree_detail.xpath('//div[@class="pharmacy-hours"]//p/text()')
              i = 0
              count = len(h_list)
              for h in h_list:
                if i < count - 2:
                  hours += h.strip() + ', '
                else:
                  hours += h.strip()
              hours = hours.split(', Emergencies:')[0].strip()
            item['store_hours'] = hours
            item['country'] = 'United States'
            yield item
        self.driver.get(init_url)
      else:
        pass

  def validate(self, item):
    try:
      return item.replace('\n', '').strip()
    except:
      return ''