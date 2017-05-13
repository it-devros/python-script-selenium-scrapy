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

class aromaespressobarcanada(scrapy.Spider):
	name = 'aromaespressobarcanada'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'https://aroma.ca/wp-admin/admin-ajax.php?action=show_all_store'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = json.loads(response.body)
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store['store'])
			item['address'] = self.validate(store['address'])
			item['address2'] = self.validate(store['address2'])
			item['city'] = self.validate(store['city'])
			item['state'] = self.validate(store['state'])
			item['zip_code'] = self.validate(store['zip'])
			item['country'] = 'Canada'
			item['phone_number'] = self.validate(store['phone'])
			item['latitude'] = self.validate(store['lat'])
			item['longitude'] = self.validate(store['lng'])
			item['store_hours'] = self.validate(store['hours'])
			yield item			

	def validate(self, item):
		try:
			item = item.strip().replace('<p>', '').replace('</p>', '').replace('=', ' ')
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''