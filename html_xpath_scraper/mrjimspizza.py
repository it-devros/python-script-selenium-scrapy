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

class mrjimspizza(scrapy.Spider):
	name = 'mrjimspizza'
	domain = 'http://www.mrjims.pizza/'
	history = []

	def start_requests(self):
		init_url = 'http://www.mrjims.pizza/storepages.cfm'
		yield scrapy.Request(url=init_url, callback=self.body) 
		yield scrapy.Request(url='http://www.mrjims.pizza/037.cfm', callback=self.parse_page) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//select[@class="storeSelect"]//option/@value').extract()
		for store in store_list:
			if store != '':
				store_url = self.domain + store + '.cfm'
				yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		try:
			item = ChainItem()
			detail = response.xpath('//div[@id="StoreTopR"]')
			namephone= detail.xpath('.//div[@class="RegBlack"][1]/text()').extract()
			np_info = []
			for np in namephone:
				if np != '':
					np_info.append(np)
			item['store_name'] = self.validate(np_info[1])
			item['address'] = self.validate(detail.xpath('.//div[@class="Paragraph"][1]/text()').extract_first())
			item['address2'] = self.validate(detail.xpath('.//div[@class="Paragraph"][2]/text()').extract_first())
			addr = self.validate(detail.xpath('.//div[@class="Paragraph"][3]/text()').extract_first()).split(',')
			item['city'] = self.validate(addr[0].strip())
			item['state'] = self.validate(addr[1].strip().split(' ')[0].strip())
			item['zip_code'] = self.validate(addr[1].strip().split(' ')[1].strip())
			item['country'] = 'United States'
			item['phone_number'] = self.validate(np_info[2]).split('Store Phone:')[1]
			h_temp = ''
			week_list = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
			cnt = 0
			hour_list = detail.xpath('//div[@class="Paragraph12"][2]//text()').extract()
			for hour in hour_list:
				if self.validate(hour) != '' and len(self.validate(hour)) < 25:
					h_temp += week_list[cnt] + ' ' + self.validate(hour).replace('to', '-') + ', '
					cnt += 1
			item['store_hours'] = h_temp[:-2]
			yield item			
		except:
			pdb.set_trace()

	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''