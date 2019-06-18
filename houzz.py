# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from houzz.items import HouzzItem
import pdb


class HouzzSpider(scrapy.Spider):
	name = 'houzz'
	allowed_domain = 'https://www.houzz.es'
	start_url = 'https://www.houzz.es/professionals'
	done_list = []

	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.parse_category)


	def parse_category(self, response):
		curl_list = response.xpath('//li[@class="sidebar-item"]/a[@class="sidebar-item-label"]/@href').extract()
		for curl in curl_list:
			if curl != 'https://www.houzz.es/professionals':
				url = curl
				param = {
					'root_url': curl
				}
				yield scrapy.Request(url=url, callback=self.parse_list, meta=param)


	def parse_list(self, response):
		pro_list = response.xpath('//div[@compid="uniprof"]//a[@class="pro-title"][1]/@href').extract()
		if pro_list:
			for pro in pro_list:
				if pro != 'javascript:;':
					yield scrapy.Request(url=pro, callback=self.parse_professional)

		next_btn = response.xpath('//a[@class="navigation-button next"]')
		if next_btn:
			url = next_btn.xpath('./@href').extract_first()
			param = {
				'root_url': response.meta['root_url']
			}
			yield scrapy.Request(url=url, callback=self.parse_list, meta=param)


	def parse_professional(self, response):
		json_scripts = response.xpath('//script[@type="application/ld+json"][1]/text()').extract_first()
		pro = json.loads(json_scripts)

		try:
			pro = pro[0]

			item = HouzzItem()
			
			item['name'] = ''

			item['telephone'] = ''
			item['website'] = ''
			item['sms'] = ''
			item['email'] = ''

			item['streetAddress'] = ''
			item['addressLocality'] = ''
			item['addressRegion'] = ''
			item['addressCountry'] = ''
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
			item['website'] = response.xpath('//a[@compid="Profile_Website"]/@href').extract_first()

			item['streetAddress'] = pro['address']['streetAddress']
			item['addressLocality'] = pro['address']['addressLocality']
			item['addressRegion'] = pro['address']['addressRegion']
			item['addressCountry'] = pro['address']['addressCountry']
			item['postalCode'] = pro['address']['postalCode']

			item['category'] = response.xpath('//span[@itemprop="child"]//span[@itemprop="title"]/text()').extract_first()
			info_list = response.xpath('//div[@class="professional-info-content"]/text()').extract()
			temp = ''
			for info in info_list:
				temp = temp + info + ', '
			item['information'] = temp[:-2]
			item['ratingstars'] = pro['aggregateRating']['ratingValue']

			yield item
		except:
			pass
			