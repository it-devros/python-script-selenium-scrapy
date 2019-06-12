# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from first.items import FirstItem
import pdb


class QuadrilleSpider(scrapy.Spider):
	name = 'quadrille'
	allowed_domain = 'https://www.source4interiors.com'
	root_url = 'https://www.source4interiors.com/brands/quadrille-1?per_page=36&page='


	def start_requests(self):
		i = 1
		while i < 30:
			url = self.root_url + str(i)
			yield scrapy.Request(url=url, callback=self.parse_list)
			i = i + 1


	def parse_list(self, response):
		json_str = ''
		try:
			json_str = response.body.split('<product-frontend-list :products="')[1].split('" :per-page="36"></product-frontend-list>')[0]
		except Exception as err:
			print err

		if json_str != '':
			json_str = self.validateStr(json_str)
			element_list = json.loads(json_str)
			for element in element_list['data']:
				item = FirstItem()

				item['sku'] = element['sku']
				item['category'] = ''
				if 'Fabric' in element['sku']:
					item['category'] = 'Fabric'
				if 'Wallpaper' in element['sku']:
					item['category'] = 'Wallpaper'
				item['name'] = element['name']
				item['price'] = element['our_price']['decimal']

				yield item


	def validateStr(self, str):
		try:
			return str.replace('&quot;', '"').strip()
		except Exception as validateErr:
			print validateErr
			return ''
