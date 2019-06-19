# -*- coding: utf-8 -*-
import scrapy
import json
from Wipo.items import WipoItem
import math
import pdb


class WipoSpider(scrapy.Spider):

	name = 'wipo'
	allowed_domain = 'http://www.wipo.int/branddb/en/'

	start_url = "http://www.wipo.int/branddb/en/"
	search_url = "http://www.wipo.int/branddb/jsp/select.jsp"


	def start_requests(self):
		url =  self.start_url
		yield scrapy.Request(url=url, callback=self.startParse)


	def startParse(self, response):
		url = self.search_url
		index = 0
		while index < 3:
			formdata = {
				"qz": "N4IgLgngDgpiBcIBGAnAhgOwCYgDQgBs0EQYM8QBHASxIAYBaMOgMwGoArAFQEEAFGACYCATgBSAWQDySAMIBxeQHcAHit4AtDQFUAQgHYAShwIBmLABkArgFEWAZUEA1JdoC8FSlZjeEARgBfIAAA=="
			}
			yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.parseList)
			index += 1



	def parseList(self, response):
		body = json.loads(response.body)
		try:
			for doc in body['response']['docs']:
				item = WipoItem()
				try:
					temp = ""
					for t in doc['BRAND']:
						temp += t + " "
					item['brand'] = self.validateStr(temp)
				except:
					item['brand'] = ""

				try:
					item['source'] = self.validateStr(doc['SOURCE'])
				except:
					item['source'] = ""
				try:
					item['status'] = self.validateStr(doc['STATUS'])
				except:
					item['status'] = ""
				try:
					item['relevance'] = self.validateStr(doc['score'])
				except:
					item['relevance'] = ""
				try:
					item['origin'] = self.validateStr(doc['OO'])
				except:
					item['origin'] = ""

				try:
					temp = ""
					for t in doc['HOL']:
						temp += t + " "
					item['holder'] = self.validateStr(temp)
				except:
					item['holder'] = ""

				try:
					item['number'] = self.validateStr(doc['ID'].replace(doc['SOURCE'], "").replace(".", ""))
				except:
					item['number'] = ""
				try:
					item['app_date'] = self.validateStr(doc['AD'])
				except:
					item['app_date'] = ""

				try:
					temp = ""
					for vc in doc['VCS']:
						temp += "VC." + vc + ", "
					item['image_class'] = self.validateStr(temp)
				except:
					item['image_class'] = ""

				try:
					temp = ""
					for nc in doc['NC']:
						temp += nc + ", "
					item['nice_CI'] = self.validateStr(temp)
				except:
					item['nice_CI'] = ""

				try:
					item['image'] = self.validateStr(doc['IMG'])
				except:
					item['image'] = ""

				yield item				
		except:
			print "=============== error detected =================="



	def validateStr(self, string):
		try:
			return string.strip()
		except:
			return False


	def eliminateTextList(self, param):
		data = []
		for item in param:
			temp = self.validateStr(item)
			if temp:
				data.append(temp)
		return data