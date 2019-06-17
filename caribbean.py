# -*- coding: utf-8 -*-
import scrapy
import json
from TripAdvisor.items import TripadvisorItem
from TripAdvisor.items import CityItem
import pdb


class CaribbeanSpider(scrapy.Spider):
	name = 'caribbean'
	allowed_url = 'https://www.tripadvisor.com'
	city_list = []

	def __init__(self):
		with open('Cities/caribbeanCity.json', 'r') as f:
			for line in f:
				temp = self.validateCityUrl(line)
				if temp != '[' and temp != ']':
					self.city_list.append(json.loads(temp))


	def start_requests(self):
		for city in self.city_list:
			url = city['url']
			yield scrapy.Request(url=url, callback=self.parseAttractions)


	def parseAttractions(self, response):
		attractions = response.xpath("//div[@id='FILTERED_LIST']//div[@class='attraction_clarity_cell']")
		for attraction in attractions:
			temp = self.validateStr(attraction.xpath(".//a/@href").extract_first())
			detail_url = self.allowed_url + temp
			if 'Review' in detail_url:
				yield scrapy.Request(url=detail_url, callback=self.parseDetail)
			else:
				yield scrapy.Request(url=detail_url, callback=self.parseStore)

		paginations = response.xpath("//div[@class='pagination']/div/a")
		for pagination in paginations:
			label = pagination.xpath("./text()").extract_first()
			label = self.validateStr(label)
			if label == 'Next':
				url = self.allowed_url + self.validateStr(pagination.xpath("./@href").extract_first())
				url = self.validateStr(url.replace('#FILTERED_LIST', ''))
				yield scrapy.Request(url=url, callback=self.parseAttractions)


	def parseStore(self, response):
		attractions = response.xpath("//div[@id='FILTERED_LIST']//div[@class='attraction_element']")
		for attraction in attractions:
			temp = self.validateStr(attraction.xpath(".//div[@class='listing_info']/a/@href").extract_first())
			detail_url = self.allowed_url + temp
			if 'Review' in detail_url:
				yield scrapy.Request(url=detail_url, callback=self.parseDetail)

		paginations = response.xpath("//div[@class='pagination']/div/a")
		for pagination in paginations:
			label = pagination.xpath("./text()").extract_first()
			label = self.validateStr(label)
			if label == 'Next':
				url = self.allowed_url + self.validateStr(pagination.xpath("./@href").extract_first())
				url = self.validateStr(url.replace('#FILTERED_LIST', ''))
				yield scrapy.Request(url=url, callback=self.parseAttractions)



	def parseDetail(self, response):
		url = response.request.url
		thing_to_do = self.validateStr(response.xpath("//h1[@id='HEADING']/text()").extract_first())

		addr_list = response.xpath("//div[@class='detail_section address']/span/text()").extract()
		address = ''
		for addr in addr_list:
			address = address + self.validateStr(addr) + ' '
		address = self.validateStr(address)
		city = self.validateCityUrl(response.xpath("//span[@class='locality']/text()").extract_first())

		phone_list = response.xpath("//div[@class='blEntry phone']/span/text()").extract()
		phone_number = ''
		for phone in phone_list:
			phone_number = phone_number + self.validateStr(phone) + ' '
		phone_number = self.validateStr(phone_number)
		email = ''
		num_review = self.validateStr(response.xpath("//span[@property='count']/text()").extract_first())
		num_rating = self.validateStr(response.xpath("//span[@class='overallRating']/text()").extract_first())

		is_bookable = False
		activities = response.xpath("//div[@class='ui_link']")
		if activities:
			is_bookable = True
			for activity in activities:
				label = self.validateStr(activity.xpath(".//div[@class='MultiTourOffer__title_container--3SBSu']//span[@class='MultiTourOffer__title--4PROg']/text()").extract_first())
				price = self.validateStr(activity.xpath(".//div[@class='MultiTourOffer__price_container--1yJni']//span[@class='fromPrice']/text()").extract_first())
				item = TripadvisorItem()
				item['url'] = url
				item['thing_to_do'] = thing_to_do
				item['address'] = address
				item['city'] = city
				item['phone_number'] = phone_number
				item['email'] = ''
				item['num_review'] = num_review
				item['num_rating'] = num_rating
				item['is_bookable'] = is_bookable
				item['activity'] = label
				item['price'] = price
				yield item

				# show more button actions

		else:
			item = TripadvisorItem()
			item['url'] = url
			item['thing_to_do'] = thing_to_do
			item['address'] = address
			item['city'] = city
			item['phone_number'] = phone_number
			item['email'] = ''
			item['num_review'] = num_review
			item['num_rating'] = num_rating
			item['is_bookable'] = is_bookable
			item['activity'] = ''
			item['price'] = ''
			yield item



	def validateCityUrl(self, string):
		try:
			return string.replace(',', '').strip()
		except:
			return ''

	def validateStr(self, string):
		try:
			return string.strip()
		except:
			return ''