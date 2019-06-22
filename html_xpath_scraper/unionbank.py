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

class unionbank(scrapy.Spider):
  name = 'unionbank'
  domain = 'https://www.unionbank.com/'
  history = []

  def start_requests(self):
    init_url = 'https://blw.unionbank.com/blw/branches/All-State-Branch-Page'
    yield scrapy.Request(url=init_url, callback=self.state) 

  def state(self, response):
    link_list = response.xpath('//div[@class="all-locations-stateOrCity-name"]//a')
    if link_list:
      for link in link_list:
        added_link = link.xpath('./@href').extract_first()
        if added_link:
          request_url = 'https://blw.unionbank.com' + added_link
          yield scrapy.Request(url=request_url, callback=self.city)
        else:
          pass
    else:
      pass 

  def city(self, response):
    page_list = response.xpath('//a[@class="page-number"]')
    if page_list:
      count = len(page_list)
      i = count - 1
      while i >= 0:
        added_link = page_list[i].xpath('./@href').extract_first()
        if added_link:
          request_url = 'https://blw.unionbank.com' + added_link
          yield scrapy.Request(url=request_url, callback=self.body)
        else:
          pass
        i -= 1
    else:
      link_list = response.xpath('//div[@id="city-list"]//a')
      if link_list:
        for link in link_list:
          added_link = link.xpath('./@href').extract_first()
          if added_link:
            request_url = 'https://blw.unionbank.com' + added_link
            yield scrapy.Request(url=request_url, callback=self.detail)
          else:
            pass
      else:
        pass

  def body(self, response):
    link_list = response.xpath('//div[@id="city-list"]//a')
    if link_list:
      for link in link_list:
        added_link = link.xpath('./@href').extract_first()
        if added_link:
          request_url = 'https://blw.unionbank.com' + added_link
          yield scrapy.Request(url=request_url, callback=self.detail)
        else:
          pass
    else:
      pass

  def detail(self, response):
    store_list = response.xpath('//div[@id="branchDetails"]//ul')
    if store_list:
      for store in store_list:
        info_list = store.xpath('./li/text()').extract()
        if info_list:
          item = ChainItem()
          item['store_name'] = self.validate(info_list[1])
          item['address'] = self.validate(info_list[2])
          item['city'] = self.validate(info_list[3])
          item['state'] = self.validate(info_list[4])
          item['zip_code'] = self.validate(info_list[5])
          item['phone_number'] = self.validate(info_list[6])
          phone_length = len(item['phone_number'])
          if phone_length > 15:
            item['phone_number'] = ''
          total_count = len(info_list)
          item['longitude'] = self.validate(info_list[total_count - 2])
          item['latitude'] = self.validate(info_list[total_count - 1])
          item['country'] = 'United States'
          s_hour_list = store.xpath('.//li//table//tr//td[@valign="top"]')
          try:
            label_list = s_hour_list[0].xpath('./text()').extract()
            hour_list = s_hour_list[1].xpath('./text()').extract()
            i = 0
            count = len(label_list)
            hours = ''
            for label in label_list:
              label = self.validate(label)
              if label:
                if i < count - 1:
                  hours += label + ' ' + self.validate(hour_list[i]) + ','
                else:
                  hours += label + ' ' + self.validate(hour_list[i])
              else:
                pass
              i += 1
            item['store_hours'] = hours
            yield item
          except:
            pass
        else:
          pass
    else:
      pass

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''