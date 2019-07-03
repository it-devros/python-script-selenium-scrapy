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

class earlsrestaurants(scrapy.Spider):
  name = 'earlsrestaurants'
  domain = 'https://earls.ca/'
  history = []

  def start_requests(self):
    
    init_url = 'https://earls.ca/locations'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    country_list = response.xpath('//div[@class="column-fallback"]')
    for country in country_list:
      store_list = country.xpath('.//li//a/@href').extract()
      countrycode = self.validate(country.xpath('./h3/text()'))
      for store in store_list:
        store_url = self.domain + store
        yield scrapy.Request(url=store_url, callback=self.parse_page, meta={'country':countrycode})

  def parse_page(self, response):
    item = ChainItem()
    detail = response.xpath('//div[@class="location-detail text-center"]')
    item['store_name'] = self.validate(detail.xpath('.//h2[@class="location-detail-heading"]//span/text()'))
    address = detail.xpath('.//p/text()').extract()[0].strip()
    item['address'] = address.split(',')[0].strip()
    addr = address.split(',')[1].strip().split(' ')
    item['city'] = ''
    for cnt in range(0, len(addr)-1):
      item['city'] += addr[cnt] + ' '
    item['state'] = addr[len(addr)-1]
    item['country'] = response.meta['country']
    item['phone_number'] = self.validate(detail.xpath('.//a[@class="phone-reserve"]/text()'))
    h_temp = ''
    hour_list = response.xpath('//div[@class="hours-expanded-details"]')
    for hour in hour_list:
      h_temp += self.validate(hour.xpath('.//span[1]/text()')) + ' ' + self.validate(hour.xpath('.//span[2]/text()')) + ', '
    item['store_hours'] = h_temp[:-2]
    yield item			

  def validate(self, item):
    try:
      return item.extract_first().strip()
    except:
      return ''