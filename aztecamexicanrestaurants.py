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

class aztecamexicanrestaurants(scrapy.Spider):
	name = 'aztecamexicanrestaurants'
	domain = ''
	history = []

	def start_requests(self):
		init_url = 'http://www.aztecamex.com/order-online/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//table//p')
		for store in store_list:
			try:
				item = ChainItem()
				detail = store.xpath('.//text()').extract()
				if len(detail) > 1:
					info = []
					for tmp in detail:
						if tmp.strip() != '':
							info.append(tmp)
					item['store_name'] = self.validate(info[0])
					item['address'] = self.validate(info[1])
					addr = self.validate(info[2]).split(',')
					item['city'] = self.validate(addr[0].strip())
					item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
					item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
					item['country'] = 'United States'
					item['phone_number'] = self.validate(info[3]).split('phone')[0].strip()
					yield item			
			except:
				pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''