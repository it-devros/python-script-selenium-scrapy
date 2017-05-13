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

class americanbodyworks(scrapy.Spider):
	name = 'americanbodyworks'
	domain = ''
	history = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/cities.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		init_url = 'http://americanbodyworks.com/wp-content/plugins/store-locator/sl-xml.php'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		with open('response.html', 'wb') as f:
			f.write(response.body)
		store_list = response.xpath('//marker')	
		for store in store_list:
			item = ChainItem()
			detail = self.validate(store.xpath('./@number')).split(' ')
			item['store_name'] = self.validate(store.xpath('./@name'))
			item['address'] = self.validate(store.xpath('./@street'))
			item['address2'] = self.validate(store.xpath('./@street2'))
			item['city'] = self.validate(store.xpath('./@city'))
			item['state'] = self.validate(store.xpath('./@state'))
			item['zip_code'] = self.validate(store.xpath('./@zip'))
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('./@phone'))
			item['latitude'] = self.validate(store.xpath('./@lat'))
			item['longitude'] = self.validate(store.xpath('./@lng'))
			item['store_hours'] = self.validate(store.xpath('./@hours'))
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip().replace('&#44;', ',').replace('%2C', ', ')
		except:
			return ''