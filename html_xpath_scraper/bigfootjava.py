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

class bigfootjava(scrapy.Spider):
	name = 'bigfootjava'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'http://www.bigfootjava.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		
		store_list = response.xpath('//select[@id="LinkMenu"]//option/@value').extract()
		for store in store_list:
			yield scrapy.Request(url=store, callback=self.parse_page)

	def parse_page(self, response):
		detail = response.xpath('//td[@class="med"]/text()').extract()
		try:
			info = []
			for tmp in detail:
				if tmp.strip() != '':
					info.append(tmp)
			item = ChainItem()
			item['store_name'] = self.validate(response.xpath('//td[@class="med"]/div[@class="Brown"]/text()').extract_first())
			item['address'] = self.validate(info[1])
			addr = self.validate(info[2]).split(',')
			try:
				item['city'] = self.validate(addr[0].strip())
				item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
				item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			except:
				tmp = self.validate(addr[0].strip()).split(' ')
				item['city'] = ''
				for cnt in range(0, len(tmp)-1):
					item['city'] += self.validate(tmp[cnt])
				item['state'] = self.validate(tmp[len(tmp)-1])
				item['zip_code'] = self.validate(addr[1].strip())

			item['country'] = 'United States'
			try:
				item['phone_number'] = self.validate(info[3])
			except:
				pass
			yield item			
		except:
			pass

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''