# -*- coding: utf-8 -*-
import scrapy
import json
from OilFilters.items import OilfiltersItem
import pdb


class Mobil3Spider(scrapy.Spider):
	name = 'mobil3'
	allowed_domain = 'https://mobiloil.com'
	start_url = 'https://mobiloil.com/en/product-selector'

	def start_requests(self):
		url = 'https://mobiloil.com/en/api/v1/vehicles/years'
		yield scrapy.Request(url=url, callback=self.parse_years)

	def parse_years(self, response):
		year_list = json.loads(response.body)
		for year in year_list:
			url = 'https://mobiloil.com/en/api/v1/vehicles/makes/' + year['Yearid']
			yield scrapy.Request(url=url, callback=self.parse_makes)

	def parse_makes(self, response):
		urlList = response.url.split('/')
		length = len(urlList)
		year = urlList[length - 1]
		make_list = json.loads(response.body)
		for make in make_list:
			url = 'https://mobiloil.com/en/api/v1/vehicles/models/' + year + '/' + make['Makename']
			yield scrapy.Request(url=url, callback=self.parse_models)

	def parse_models(self, response):
		urlList = response.url.split('/')
		length = len(urlList)
		year = urlList[length - 2]
		make = urlList[length - 1]
		model_list = json.loads(response.body)
		for model in model_list:
			item = OilfiltersItem()
			item['year'] = year
			item['make'] = make
			item['model'] = model['Modelname']
			item['types'] = []
			item['filters'] = []
			yield item
