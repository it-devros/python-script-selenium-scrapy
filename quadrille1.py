# -*- coding: utf-8 -*-
from __future__ import absolute_import
import scrapy
import json
from second.items import SecondItem
import pdb


class QuadrilleSpider(scrapy.Spider):
	name = 'quadrille'
	allowed_domain = 'http://store.lynnchalk.com'
	root_url = 'http://store.lynnchalk.com/quadrille/?sort=featured&page='


	def start_requests(self):
		i = 1
		while i < 100:
			url = self.root_url + str(i)
			yield scrapy.Request(url=url, callback=self.parse_list)
			i = i + 1


	def parse_list(self, response):
		url_list = response.xpath('//div[@class="product-item-details"]/a/@href').extract()
		for url in url_list:
			yield scrapy.Request(url=url, callback=self.parse_element)


	def parse_element(self, response):
		item = SecondItem()
		item['name'] = self.validateStr(response.xpath('//h1[@class="product-title"]/text()').extract_first())
		if 'Wallpaper' in item['name']:
			item['category'] = 'Wallpaper'
		else:
			item['category'] = 'Fabric'
		item['price'] = self.validateStr(response.xpath('//span[@class="price-value"]/text()').extract_first())
		item['sku'] = self.validateStr(response.xpath('//dd[@itemprop="sku"]/text()').extract_first())
		if item['price']:
			item['price'] = item['price'].replace('$', '')

		yield item


	def validateStr(self, str):
		try:
			return str.strip()
		except Exception as validateErr:
			print validateErr
			return ''
