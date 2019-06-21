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
import pdb
import unicodedata

class californiatortilla(scrapy.Spider):
	name = 'californiatortilla'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'http://californiatortilla.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//form[@id="location_nav"]//option/@value').extract()
		for store in store_list:
			if store != '#':
				yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//div[@id="content"]/h2/text()').extract_first())
		item['coming_soon'] = '0'
		if 'Coming Soon' in item['store_name']:
			item['store_name'] = item['store_name'].split('Coming Soon')[0].strip()
			item['coming_soon'] = '1'
		detail = response.xpath('//div[@id="location_information"]')
		address = detail.xpath('.//div[@id="address"]//p/text()').extract()
		item['address'] = self.validate(address[0])
		item['address2'] = ''
		addr = address[1].strip().split(',')
		item['city'] = self.validate(addr[0].strip())
		item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
		try:
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
		except:
			pass			
		item['country'] = 'United States'
		item['phone_number'] = self.validate(detail.xpath('.//p/span[@class="phone"]/text()').extract_first())
		h_temp = ''
		hour_list = detail.xpath('.//div[@id="hours"]//li')
		for hour in hour_list:
			hour = hour.xpath('.//text()').extract()
			h_temp += self.validate(hour[0]) + ' ' + self.validate(hour[1]) + ', '
		item['store_hours'] = h_temp[:-2]
		item['store_type'] = ''
		item['other_fields'] = ''
		yield item			

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''