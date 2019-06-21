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
import usaddress

class blastfitness(scrapy.Spider):
	name = 'blastfitness'
	domain = 'http://www.blastfitness.com'
	history = []

	def start_requests(self):
		init_url = 'http://www.blastfitness.com/locations/'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		store_list = response.xpath('//article[contains(@class, "featured-list")]//a/@href').extract()
		for store in store_list:
			store_url = self.domain + store
			yield scrapy.Request(url=store_url, callback=self.parse_page)

	def parse_page(self, response):
		item = ChainItem()
		item['store_name'] = self.validate(response.xpath('//h2/text()').extract_first())
		address = self.validate(response.xpath('//article[contains(@class, "singe-location--contentarea")]//strong/text()').extract_first())
		item['address'] = ''
		item['city'] = ''
		addr = usaddress.parse(address)
		for temp in addr:
			if temp[1] == 'PlaceName':
				item['city'] += temp[0].replace(',','')	+ ' '
			elif temp[1] == 'StateName':
				item['state'] = temp[0].replace(',','')
			elif temp[1] == 'ZipCode':
				item['zip_code'] = temp[0].replace(',','')
			else:
				item['address'] += temp[0].replace(',','') + ' '
		item['country'] = 'United States'
		item['phone_number'] = self.validate(response.xpath('//span[@class="single-location--phone"]/text()').extract_first())
		h_temp = ''
		hour_list = response.xpath('//div[contains(@class, "hours--left")]//div[@class="columns"]')
		for hour in hour_list:
			hour = hour.xpath('.//text()').extract()
			for tmp in hour:
				if tmp.strip() != '':
					h_temp += self.validate(tmp) + ' '
			h_temp += ', '
		item['store_hours'] = h_temp[:-2]
		yield item		

	def validate(self, item):
		try:
			return unicodedata.normalize('NFKD', item).encode('ascii','ignore').strip()
		except:
			return ''