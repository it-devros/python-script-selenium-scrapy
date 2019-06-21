
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

class NauticaSpider(scrapy.Spider):
	name = 'nautica'
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
		form_data = {
			'dwfrm_storelocator_countryCode':'US',
			'dwfrm_storelocator_distanceUnit':'mi',
			'dwfrm_storelocator_postalCode':'10001',
			'dwfrm_storelocator_maxdistance':'999999.0',
			'dwfrm_storelocator_findbyzip':'Search'
		}
		yield  FormRequest(url="http://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-Find/C562088103", formdata=form_data, headers=self.headers, callback=self.parse_store)


	def parse_store(self, response):

		# for city, row in self.citiesusca.items():
		self.driver.get("http://www.nautica.com/on/demandware.store/Sites-nau-Site/default/Stores-Find")

		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)
		zipcode = self.driver.find_element_by_name("dwfrm_storelocator_postalCode")

		zipcode.send_keys("10001")

		# self.driver.find_element_by_id("s2id_dwfrm_storelocator_maxdistance").click()
		#
		# self.driver.find_element_by_xpath('//div[contains(@class, "select2-drop")]/ul/li[4]').click()

		self.driver.find_element_by_id('dwfrm_storelocator_maxdistance').send_keys('USA')

		self.driver.find_element_by_name("dwfrm_storelocator_findbyzip").click()

		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)

		self.driver.close()
		with open('dump', 'wb') as f:
			 f.write(source)
		for store in tree.xpath('//div[contains(@class,"store-location-results-box")]/table/tbody/tr'):
			item = ChainItem()
			item['store_name'] = store.xpath('.//span[@class="name"]/text()')[0].replace('\t', '').replace('\n', '').strip()

			item['store_number'] = store.xpath('.//a[contains(@class, "editbutton")]/@href')[0].split('StoreID=')[1]
			item['address'] = store.xpath('.//a[contains(@class, "editbutton")]/text()')[1].replace('\t', '').replace('\n', '').strip()
			item['address2'] = ''
			addr = store.xpath('.//a[contains(@class, "editbutton")]/text()')[2].replace('\t', '').replace('\n', '').strip()



			if len(addr.split(',')) >= 2:
				item['city'] = addr.split(',')[0]
				item['state'] = addr.split(',')[1].strip().split(' ')[0]
				if len(addr.split(',')[1].strip().split(' ')) >= 2:
					item['zip_code'] = addr.split(',')[1].strip().split(' ')[1]
				else:
					item['zip_code'] = ''
			else:
				item['city'] = addr
				item['state'] = ''
				item['zip_code'] = ''
			try:
				item['country'] = store.xpath('.//a[contains(@class, "editbutton")]/text()')[3].replace('\t', '').replace('\n', '').strip()
			except:
				item['country'] = "United States"
			item['phone_number'] = store.xpath('.//td[contains(@class, "store-phone")]/text()')[0].replace('\t', '').replace('\n', '').strip()

			item['latitude'] = ''
			item['longitude'] = ''

			item['store_hours'] = store.xpath('.//td[contains(@class, "store-hours")]/text()')[0].replace('\t', '').replace('\n', '').strip()
			if item['store_hours'] == 'Not Available':
				item['store_hours'] = ''

			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = '0'
			if item['store_number'] not in self.history:
				self.history.append(item['store_number'])
				yield item


	def validate(self, xpath_obj):
		try:
			return xpath_obj.extract_first().strip()
		except:
			return ""



		
