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

class guessinternational(scrapy.Spider):
	name = 'guessinternational'
	domain = 'http://www.guess.com'
	history = []
	us_location_list = []
	ca_location_list = []
	location_list = []

	def __init__(self):
		script_dir = os.path.dirname(__file__)
		file_path = script_dir + '/geo/US_Cities.json'
		with open(file_path) as data_file:    
			self.us_location_list = json.load(data_file)
		file_path = script_dir + '/geo/CA_Cities.json'
		with open(file_path) as data_file:    
			self.ca_location_list = json.load(data_file)
		file_path = script_dir + '/geo/countries.json'
		with open(file_path) as data_file:    
			self.location_list = json.load(data_file)

	def start_requests(self):
		header = {
			"Accept":"application/json, text/javascript, */*; q=0.01",
			"Accept-Encoding":"gzip, deflate, br",
			"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
			"X-Requested-With":"XMLHttpRequest"
		}
		for location in self.us_location_list:
			init_url = 'https://api.guess.com/rest/1.0/Store/GetByCoordinate?latitude=%s&longitude=%s&storeConceptType=&radius=100' % (str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, headers=header, callback=self.body)
		for location in self.ca_location_list:
			init_url = 'https://api.guess.com/rest/1.0/Store/GetByCoordinate?latitude=%s&longitude=%s&storeConceptType=&radius=100' % (str(location['latitude']), str(location['longitude']))
			yield scrapy.Request(url=init_url, headers=header, callback=self.body)
		for location in self.location_list:
			init_url = 'https://api.guess.com/rest/1.0/Store/GetByCoordinate?latitude=%s&longitude=%s&storeConceptType=&radius=1000' % (str(location[1]), str(location[2]))
			yield scrapy.Request(url=init_url, headers=header, callback=self.body)

	def body(self, response):
		store_list = json.loads(response.body)
		store_list = store_list['Result']
		if store_list:
			for store in store_list:
				if not self.validate(store['StoreNumber']) in self.history:
					self.history.append(self.validate(store['StoreNumber']))
					item = ChainItem()
					try:
						item['store_hours'] = self.validate(store['TimeOfOperation'].replace('\\', ', '))
					except:
						pass
					item['store_name'] = self.validate(store['Name'])
					item['store_number'] = self.validate(store['StoreNumber'])
					item['country'] = self.validate(store['Country'])
					item['state'] = self.validate(store['StateProvince'])
					item['zip_code'] = self.validate(store['PostalCode'])
					item['city'] = self.validate(store['City'])
					item['address'] = self.validate(store['AddressLine1'])
					item['address2'] = self.validate(store['AddressLine2'])
					item['phone_number'] = self.validate(store['PhoneNumber'])
					item['latitude'] = self.validate(str(store['Latitude']))
					item['longitude'] = self.validate(str(store['Longitude']))
					yield item

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''