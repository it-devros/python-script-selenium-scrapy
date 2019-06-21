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
import unicodedata
import pdb

class billysimsbbq(scrapy.Spider):
	name = 'billysimsbbq'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.billysimsbbq.com/all-locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		store_list = response.xpath('//li[@class="location"]//span[@class="location-name"]//a/@href').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		try:
			detail = response.xpath('//div[@id="content"]')
			item = ChainItem()
			item['store_name'] = self.validate(detail.xpath('./h1//text()').extract_first())
			address = detail.xpath('//span[@class="location-address"]/text()').extract()
			item['address'] = self.validate(address[1].strip())
			addr = address[2].strip().split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(detail.xpath('.//span[@class="location-phone"]/text()').extract_first())
			h_temp =''
			hour_list = detail.xpath('./p/text()').extract()
			for hour in hour_list:
				if ':' in hour:
					h_temp += self.validate(hour) + ', '
			if h_temp[0:1] == ':':
				item['store_hours'] = h_temp[2:-2]
			else:
				item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pdb.set_trace()	

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''