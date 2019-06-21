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

class charterfitness(scrapy.Spider):
	name = 'charterfitness'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'http://www.charterfitness.com/locations/find-a-location/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)
		state_list = response.xpath('//select[@name="state"]//option/@value').extract()
		for state in state_list:
			if state != '':
				state_url = 'http://www.charterfitness.com/locations/find-a-location/?state=%s&miles=50' % state
				yield scrapy.Request(url=state_url, callback=self.parse_page)
# 
	def parse_page(self, response):
		store_list = response.xpath('//table[@id="location_list"]//tr')
		for store in store_list:
			try:
				item = ChainItem()
				item['store_name'] = self.validate(store.xpath('.//td[1]//a[1]/text()').extract_first())
				address = store.xpath('.//td[2]/text()').extract()
				item['address'] = self.validate(address[0])
				item['city'] = self.validate(address[1]).split(',')[0].strip()
				item['state'] = self.validate(address[1]).split(',')[1].strip().split(' ')[0]
				item['zip_code'] = self.validate(address[1]).split(',')[1].strip().split(' ')[1]
				item['country'] = 'United States'
				item['phone_number'] = self.validate(address[2])
				yield item			
			except:
				pass

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''