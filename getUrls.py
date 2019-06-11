# -*- coding: utf-8 -*-
import scrapy
import json
from Autism.items import UrlItem
import time
import datetime
import pdb


class UrlSpider(scrapy.Spider):

	name = 'url'
	start_url = 'https://www.autismconnect.com/directory?view=directories'
	root_url = 'https://www.autismconnect.com'


	def start_requests(self):
		url = self.start_url
		formdata = {
			'country': 'USA',
			'state_name': '',
			'city': '',
			'category_id': ''
		}
		yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.startSearch)


	def startSearch(self, response):
		urls = self.eliminateTextList(response.xpath('//section[@class="search"]//div[@class="search-details-main"]//div[@class="search-more"]/a/@href').extract())
		for url in urls:
			if url != '':
				item = UrlItem()
				item['url'] = self.root_url + url
				yield item

		index = 20
		while index < 19660:
			url = self.start_url + '&start=' + str(index)
			formdata = {
				'country': 'USA',
				'state_name': '',
				'city': '',
				'category_id': ''
			}
			yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.startSearch)
			index += 20





	def validateStr(self, string):
		try:
			return string.strip()
		except:
			return ''


	def eliminateTextList(self, param):
		data = []
		for item in param:
			data.append(self.validateStr(item))
		return data



