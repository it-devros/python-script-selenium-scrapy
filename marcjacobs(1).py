
import scrapy
import json
import os
import time
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
import pdb
from selenium import webdriver

class MarcjacobsSpider(scrapy.Spider):
	name = 'marcjacobs'
	history = ['']
	domain = 'https://www.petsmart.ca'
	headers = {
		"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
		"X-Requested-With":"XMLHttpRequest",
		"Accept":"*/*",
		"Content-Type":"application/x-www-form-urlencoded"
	}
	driver = webdriver.Chrome("./chromedriver")

	def __init__(self):
		citiesusca   = open('citiesusca.json', 'rb')
		self.citiesusca = json.loads(citiesusca.read())

	def start_requests(self):
		yield  scrapy.Request(url="https://www.marcjacobs.com/stores", callback=self.parse_store)


	def parse_store(self, response):
		self.driver.get("https://www.marcjacobs.com/stores")  
		
		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		self.driver.find_element_by_id("dwfrm_storelocator_maxdistance").send_keys('Within 200 Miles')
		for country in tree.xpath('//select[@id="dwfrm_storelocator_address_country"]/option')[1:]:
			country = country.xpath('./text()')[0]

			self.driver.find_element_by_id("dwfrm_storelocator_address_country").send_keys(country)
			
			self.driver.find_element_by_name("dwfrm_storelocator_findstores").click()
			source = self.driver.page_source.encode("utf8")
			tree = etree.HTML(source) 

			for store in tree.xpath('//li[contains(@class,"store-grid")]/div[1]/@data-store'):
				store = json.loads(store)
				item = ChainItem()
				item['store_name'] = store['Name']
				item['store_number'] = store['ID']
				item['address'] = store['add1']
				item['address2'] = store['add2']
				item['city'] = store['city']

				item['state'] = store['state']
				item['zip_code'] = store['postalcode']

				item['country'] = country
				item['phone_number'] = store['phone']
				
				item['latitude'] = store['Lat']
				item['longitude'] = store['Long']

				item['store_hours'] = ' ; '.join(store['hours'])
				item['store_type'] = ''
				item['other_fields'] = ''
				item['coming_soon'] = '0'
				if item['store_number'] not in self.history:
					self.history.append(item['store_number'])
				yield item


		self.driver.close()
	def validate(self, xpath_obj):
		try:
			return xpath_obj.extract_first().strip()
		except:
			return ""

