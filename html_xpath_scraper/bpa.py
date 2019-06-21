# -*- coding: utf-8 -*-
import scrapy
import json
from Bpa.items import BpaItem
import math
import pdb


class BpaSpider(scrapy.Spider):
	name = 'bpa'

	allowed_domain = 'https://www.bpa.de/'
	start_url = 'https://www.bpa.de/Anbietersuche.326.0.html'

	input_zip_code = ''
	input_mile = ''


	def __init__(self, zip_code='', mile='', *args, **kwargs):
		super(BpaSpider, self).__init__(*args, **kwargs)
		self.input_zip_code = zip_code
		self.input_mile = mile


	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.startParse)


	def startParse(self, response):
		index = 0
		url =  self.start_url + '?&tx_bpapflegeeinrichtungen_pi1%5Bzip%5D=' + self.input_zip_code + '&tx_bpapflegeeinrichtungen_pi1%5Bumkreis%5D=' + self.input_mile + '.0&tx_bpapflegeeinrichtungen_pi1%5Bpointer%5D=' + str(index)
		param = {
			'index': index
		}
		yield scrapy.Request(url=url, callback=self.parseList, meta=param)


	def parseList(self, response):
		companyList = response.xpath('//div[contains(@class, "pflege-item") and contains(@class, "zebra")]')
		if len(companyList) > 0:
			for company in companyList:
				company_name = company.xpath('./div[@class="title"]/h4/text()').extract_first()
				category = company.xpath('./div[@class="title"]/b/text()').extract_first()
				contact = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[1]/text()').extract_first()
				street_number = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[2]/text()').extract_first()
				zip_town = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[3]/text()').extract_first()
				phone = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[4]/text()').extract_first()
				fax = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[5]/text()').extract_first()
				mail = company.xpath('./div[@class="pflege-item-con"]/div[@class="left"]/div[@class="mail"]/a/text()').extract_first()

				item = BpaItem()
				item['company_name'] = self.validateString(company_name)
				item['category'] = self.validateString(category)
				item['contact'] = self.validateString(contact)
				item['street_number'] = self.validateString(street_number)
				item['zip_town'] = self.validateString(zip_town)
				item['phone'] = self.validateString(phone)
				item['fax'] = self.validateString(fax)
				item['mail'] = self.validateString(mail)

				yield item

			index = response.meta['index'] + 1
			url = self.start_url + '?&tx_bpapflegeeinrichtungen_pi1%5Bzip%5D=' + self.input_zip_code + '&tx_bpapflegeeinrichtungen_pi1%5Bumkreis%5D=' + self.input_mile + '.0&tx_bpapflegeeinrichtungen_pi1%5Bpointer%5D=' + str(index)
			param = {
				'index': index
			}
			yield scrapy.Request(url=url, callback=self.parseList, meta=param)

		else:
			pass





	def validateString(self, string):
		try:
			if len(string) > 0:
				return string.strip()
			else:
				return ''
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