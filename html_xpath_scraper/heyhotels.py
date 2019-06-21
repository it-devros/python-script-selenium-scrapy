# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from Shafaqat.items import ShafaqatItem
import math
import pdb


class HeyHotelsSpider(scrapy.Spider):
	name = 'heyhotels'
	allowed_domain = 'https://heyhotels.co.za/'
	start_url = 'https://heyhotels.co.za/'
	root_url = 'https://heyhotels.co.za'
	# allowed_location_list = ['Cape_Town', 'Johannesburg', 'Pretoria', 'Durban', 'Port_Elizabeth', 'Bloemfontein']
	allowed_location_list = ['Cape_Town']

	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.parse_Start)

	def parse_Start(self, response):
		location_list = response.xpath("//ul[@class='in_vicinity']/li/span/a/@href").extract()
		for location in location_list:
			temp = self.validateCity(location)
			if temp in self.allowed_location_list:
				url = self.start_url + temp
				param = {
					'location': temp
				}
				yield scrapy.Request(url=url, callback=self.parse_Area, meta=param)

	def parse_Area(self, response):
		area_url = response.xpath("//ul[@class='in_surroundings_new']/li/a[@class='related_queries_a']/@href").extract()
		for area in area_url:
			param = {
				'page': 1,
				'location': response.meta['location'],
				'area': area
			}
			url = self.root_url + area
			yield scrapy.Request(url=url, callback=self.parse_Page, meta=param)

	def parse_Page(self, response):
		hotel_list = response.xpath("//ul[@class='venues']/li/div/div/h3/a/@href").extract()
		if hotel_list:
			for hotel in hotel_list:
				url = self.root_url + hotel
				paramDetail = {
					'location': response.meta['location']
				}
				yield scrapy.Request(url=url, callback=self.parse_Detail, meta=paramDetail)

		flag = False
		distance = ""
		btn_list = response.xpath("//div[@class='pagination']//a")
		for btn in btn_list:
			if "Next" in btn.xpath("./text()").extract_first():
				flag = True
				temp = btn.xpath("./@href").extract_first()
				distance = temp.split("&distance=")[1]

		if flag:
			page = int(response.meta['page']) + 1
			param = {
				'page': page,
				'location': response.meta['location'],
				'area': response.meta['area']
			}
			next_url = self.root_url + response.meta['area'] + "?sida=" + str(page) + "&distance=" + distance
			yield scrapy.Request(url=next_url, callback=self.parse_Page, meta=param)

	def parse_Detail(self, response):
		category = 'Hotels'
		name = self.validateStr(response.xpath("//div[@id='ca_header']/h1/text()").extract_first())

		rating = ''
		if response.xpath("//div[@id='ca_header']//span[@class='average']/text()").extract_first():
			rating = self.validateStr(response.xpath("//div[@id='ca_header']//span[@class='average']/text()").extract_first()) + "/" + self.validateStr(response.xpath("//div[@id='ca_header']//span[@class='best']/text()").extract_first())

		address = self.validateStr(response.xpath("//div[@id='ca_content']//div[@class='adr']/text()").extract_first())
		city = self.validateStr(response.xpath("//div[@id='ca_content']//div[@class='adr']/a/text()").extract_first())
		location = response.meta['location']
		phone = self.validateStr(response.xpath("//div[@id='ca_content']//div[@itemprop='telephone']/text()").extract_first())
		website = self.validateStr(response.xpath("//div[@id='ca_content']//div[@class='ca_content_info'][1]/div[6]/a[@target='_blank']/@href").extract_first())
		facebook = self.validateStr(response.xpath("//div[@id='ca_content']//div[@class='ca_content_info'][2]/div[2]/a[@target='_blank']/@href").extract_first())

		source_url = response.url

		item = ShafaqatItem()
		item['category'] = category
		item['company_name'] = name
		item['rating'] = rating
		item['address'] = address
		item['city'] = city
		item['location'] = location
		item['phone'] = phone
		item['website'] = website
		item['facebook_url'] = facebook
		item['source_url'] = source_url
		yield item


	def validateCity(self, city):
		return city.replace('/', '').strip()

	def validateStr(self, st):
		try:
			return st.strip()
		except:
			return ""


