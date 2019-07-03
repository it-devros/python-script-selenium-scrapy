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

class fitzoneforforwomen(scrapy.Spider):
  name = 'fitzoneforforwomen'
  domain = 'http://fitzoneforwomen.com'
  history = []

  def start_requests(self):
    init_url = 'http://fitzoneforwomen.com/wp-content/plugins/store-locator/sl-xml.php?mode=gen&lat=42.9275277&lng=-83.62995180000001&radius=500'
    yield scrapy.Request(url=init_url, callback=self.body) 

  def body(self, response):
    store_list = response.xpath('//markers//marker')
    if store_list:
      for store in store_list:
        request_url = store.xpath('./@url').extract_first()
        request = scrapy.Request(url=request_url, callback=self.parse_detail)
        request.meta['store_name'] = self.validateName(store.xpath('./@name').extract_first())
        request.meta['address'] = store.xpath('./@street').extract_first()
        request.meta['address2'] = store.xpath('./@street2').extract_first()
        request.meta['city'] = store.xpath('./@city').extract_first()
        request.meta['state'] = store.xpath('./@state').extract_first()
        request.meta['zip_code'] = store.xpath('./@zip').extract_first()
        request.meta['latitude'] = store.xpath('./@lat').extract_first()
        request.meta['longitude'] = store.xpath('./@lng').extract_first()
        request.meta['phone'] = store.xpath('./@phone').extract_first()
        yield request
    else:
      pass

  def parse_detail(self, response):
    hours = response.xpath('//div[@class="widget widget_text"]//ul//li/text()').extract()
    store_hours = self.getHours(hours)
    item = ChainItem()
    item['store_name'] = response.meta['store_name']
    item['address'] = response.meta['address']
    item['address2'] = response.meta['address2']
    item['city'] = response.meta['city']
    item['state'] = response.meta['state']
    item['zip_code'] = response.meta['zip_code']
    item['latitude'] = response.meta['latitude']
    item['longitude'] = response.meta['longitude']
    item['phone_number'] = response.meta['phone']
    item['store_hours'] = store_hours
    item['country'] = 'United States'
    yield item

  def getHours(self, _list):
    if _list:
      store_hours = ''
      count = len(_list)
      i = 0
      for hour in _list:
        if i < count - 1:
          store_hours += hour + ', '
        else:
          store_hours += hour
        i += 1
      return store_hours
    else:
      return ''

  def validateName(self, item):
    try:
      return item.replace('&#44;', ' ').strip()
    except:
      return ''

  def validate(self, item):
    try:
      return item.strip()
    except:
      return ''