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

class amigoskingsclassic(scrapy.Spider):
	name = 'amigoskingsclassic'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.amigoskings.com/locations'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//div[contains(@class, "views-field-nodefield")]')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//h2[@class="nodeTitleCopy"]/text()'))
			item['address'] = self.validate(store.xpath('.//div[@class="street-address"]/text()'))
			item['city'] = self.validate(store.xpath('.//span[@class="locality"]/text()'))
			item['state'] = self.validate(store.xpath('.//span[@class="region"]/text()'))
			item['zip_code'] = self.validate(store.xpath('.//span[@class="postal-code"]/text()'))
			item['country'] = 'United States'
			item['phone_number'] = self.validate(store.xpath('.//div[@class="tel"]//span[@class="value"]/text()'))
			h_temp = ''
			hour_list = store.xpath('.//span[@class="oh-display"]')
			for hour in hour_list:
				h_temp += self.validate(hour.xpath('.//span[@class="oh-display-label"]/text()')) + ' ' + self.validate(hour.xpath('.//span[contains(@class, "oh-display-times")]/text()')) + ', '
			item['store_hours'] = h_temp[:-2]
			yield item			

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''