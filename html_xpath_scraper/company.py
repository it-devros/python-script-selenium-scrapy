# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from seccion.items import SeccionItem
import pdb


class CompanySpider(scrapy.Spider):
	name = 'company'
	allowed_domain = 'https://www.seccionamarilla.com.mx'
	root_url = 'https://www.seccionamarilla.com.mx/resultados/'
	search_key = '' 

	def __init__(self, searchKey=None, *args, **kwargs):
		super(CompanySpider, self).__init__(*args, **kwargs)
		self.search_key = searchKey


	def start_requests(self):
		url = self.root_url + self.search_key + '/' + '1'
		param = {
			'index': 1,
			'root': self.root_url + self.search_key + '/'
		}
		yield scrapy.Request(url=url, callback=self.parse_list, meta=param)


	def parse_list(self, response):
		element_list = response.xpath('//ul[@class="list"]//li')
		if element_list:
			for element in element_list:
				temp_url = element.xpath('./div[@class="row l-btn-container"]/a[1]/@href').extract_first()
				url = self.allowed_domain + temp_url
				yield scrapy.Request(url=url, callback=self.parse_element)

		next_btn = response.xpath('//div[@class="pagination"]/ul/li/a[@title="Siguiente"]')
		if next_btn:
			index = response.meta['index']
			index = index + 1
			param = {
				'index': index,
				'root': response.meta['root']
			}
			url = response.meta['root'] + str(index)
			yield scrapy.Request(url=url, callback=self.parse_list, meta=param)


	def parse_element(self, response):
		name = response.xpath('//div[@class="title"]/h1[@itemprop="name"]//text()').extract_first()

		telephone = response.xpath('//span[@itemprop="telephone"]/text()').extract_first()
		website = response.xpath('//div[@class="row button-panel"]/a[1]/@href').extract_first()
		sms = ''
		temp = response.xpath('//div[@class="row button-panel"]/a[3]/@onclick').extract_first()
		if temp:
			try:
				sms = temp.split('setVarSms(')[1].split(',')[0]
			except Exception as smsErr:
				print smsErr
		email = ''
		temp = response.xpath('//div[@class="row button-panel"]/a[2]/@onclick').extract_first()
		if temp:
			try:
				email = temp.split("'")[5]
			except Exception as emailErr:
				print emailErr

		streetAddress = response.xpath('//span[@itemprop="streetAddress"]//text()').extract_first()
		addressLocality = response.xpath('//span[@itemprop="addressLocality"]//text()').extract_first()
		addressRegion = response.xpath('//span[@itemprop="addressRegion"]//text()').extract_first()
		postalCode = response.xpath('//span[@itemprop="postalCode"]//text()').extract_first()

		schedule = response.xpath('//meta[@itemprop="openingHours"]/@content').extract_first()
		category = 'Hotel'
		information = response.xpath('//p[@itemprop="description"]//text()').extract_first()
		payments = response.xpath('//div[@id="pagos"]/p/@title').extract()

		rating = 0
		temp = response.xpath('//span[@itemprop="ratingValue"]//text()').extract_first()
		if temp:
			rating = int(temp.replace('star', '')) / 10
		comments = response.xpath('//ul[@class="comments"]/li/div[@class="comment-text"]/p[@itemprop="reviewBody"]//text()').extract()
		s_tels = response.xpath('//span[@itemprop="telephone"]/text()').extract()


		item = SeccionItem()
		
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


		item['name'] = self.validateString(name)

		item['telephone'] = self.validateString(telephone)
		item['website'] = self.validateString(website)
		item['sms'] = self.validateString(sms)
		item['email'] = self.validateString(email)

		item['streetAddress'] = self.validateString(streetAddress)
		item['addressLocality'] = self.validateString(addressLocality)
		item['addressRegion'] = self.validateString(addressRegion)
		item['postalCode'] = self.validateString(postalCode)

		item['schedule'] = self.validateString(schedule)
		item['category'] = category
		item['information'] = self.validateString(information)
		item['payments'] = self.validateStrList(payments)

		item['rating'] = rating
		item['comments'] = self.validateStrList(comments)
		item['s_tels'] = self.validateString(s_tels)

		yield item


	def validateString(self, string):
		try:
			return string.strip()
		except Exception as stringErr:
			print stringErr
			return ''


	def validateStrList(self, params):
		temp = []
		try:
			for param in params:
				temp.append(param.strip())
			return temp
		except Exception as listErr:
			print listErr
			return []

