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

class blackbeardiner(scrapy.Spider):
	name = 'blackbeardiner'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'https://passport.blackbeardiner.com/api/locations?callback=callback_for_jsonp'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		with open('response.html', 'wb') as f:
			f.write(response.body)

		store_list = json.loads(response.body.split('jsonp(')[1][:-2])
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['name'])
			item['store_number'] = self.validate(str(store['store_id']))
			item['address'] = self.validate(store['street_address'])
			item['address2'] = self.validate(store['street_address_2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store['phone'])
			item['store_hours'] = self.validate(store['hours_of_operation'])			
			yield item			

	def validate(self, item):
		try:
			return item.strip().replace('\r', '').replace('\n', '')
		except:
			return ''