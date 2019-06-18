# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from homify.items import HomifyItem
import pdb

class HomifySpider(scrapy.Spider):
	name = 'homify'
	allowed_domain = 'https://www.homify.com.mx'
	root_url = 'https://www.homify.com.mx/professionals?page='

	def start_requests(self):
		i = 1
		while i < 10000:
			url = self.root_url + str(i)
			yield scrapy.Request(url=url, callback=self.parse_list)
			print '+++++++++++++ index +++++++++++++++'
			print i
			i = i + 1

	def parse_list(self, response):
		json_scripts = response.xpath('//script[@type="application/ld+json"][2]/text()').extract_first()
		if json_scripts:
			pro_list = json.loads(json_scripts)
			for pro in pro_list['ItemListElement']:
				url = pro['url']
				yield scrapy.Request(url=url, callback=self.parse_pro)
		else:
			print '+++++++++++++++++ No List here ++++++++++++++++'


	def parse_pro(self, response):
		json_scripts = response.xpath('//script[@type="application/ld+json"][2]/text()').extract_first()
		pro = json.loads(json_scripts)

		item = HomifyItem()

		item['name'] = ''

		item['telephone'] = ''
		item['website'] = ''
		item['sms'] = ''
		item['email'] = ''

		item['streetAddress'] = ''
		item['addressLocality'] = ''
		item['addressRegion'] = ''
		item['postalCode'] = ''

		item['schedules'] = ''
		item['category'] = ''
		item['information'] = ''
		item['paymentAccepted'] = ''

		item['ratingstars'] = ''
		item['comments'] = ''
		item['s_tel'] = ''


		item['name'] = pro['name']

		item['telephone'] = pro['telephone']
		item['website'] = response.xpath('//div[@class="contact"]/a[1]/text()').extract_first()
		item['email'] = pro['contactPoint']['email']

		item['streetAddress'] = pro['address']['streetAddress']
		item['addressLocality'] = pro['address']['addressLocality']
		item['addressRegion'] = pro['address']['addressCountry']
		item['postalCode'] = pro['address']['postalcode']

		item['category'] = response.xpath('//a[@class="category-city--category"][1]/text()').extract_first()
		item['information'] = self.validateStr(pro['description'])
		item['ratingstars'] = response.xpath('//a[@controller="reviews"]/b/span[1]/@data-rating').extract_first()

		yield item


	def validateStr(self, str):
		return str.replace('\n', '').replace('<p>', '').replace('</p>', '').replace('<br>', '').replace('<br/>', '')


