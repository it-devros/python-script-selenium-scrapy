import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from selenium import webdriver
from lxml import html
import pdb
import tokenize
import token
from StringIO import StringIO
import unicodedata

class brookshirebrothers(scrapy.Spider):
	name = 'brookshirebrothers'
	domain = ''
	history = []

	def start_requests(self):
		
		init_url = 'https://www.brookshirebrothers.com/store-locator?ajax=1'
		yield scrapy.Request(url=init_url, callback=self.body) 

	def body(self, response):
		print("=========  Checking.......")
		try:
			data = response.body.split('var locationCoordinates =')[1].strip()[:-9].strip()
			data = [line.decode('utf-8').strip() for line in data.readlines()]
			with open('response.html', 'wb') as f:
				f.write(data)
			# store_list = json.loads(self.fixLazyJson(data))
			# for store in store_list:
			# 	item = ChainItem()
			# 	item['store_name'] = store['name']
			# 	item['store_number'] = store['store_number']
			# 	item['address'] = store['address']
			# 	item['address2'] = store['crossStreet']
			# 	item['city'] = store['city']
			# 	item['state'] = store['state']
			# 	item['zip_code'] = store['zip']
			# 	item['country'] = store['country']
			# 	item['phone_number'] = store['phone']
			# 	item['latitude'] = store['latitude']
			# 	item['longitude'] = store['longitude']
			# 	item['store_hours'] = store['hours']
			# 	item['store_type'] = ''
			# 	item['other_fields'] = ''
			# 	item['coming_soon'] = ''
			# 	if item['store_number'] not in self.history:
			# 		self.history.append(item['store_number'])
			# 		yield item		
		except:
			pdb.set_trace()
			

	def fixLazyJson (self, in_text):
	        tokengen = tokenize.generate_tokens(StringIO(in_text).readline)

	        result = []
	        for tokid, tokval, _, _, _ in tokengen:
	            # fix unquoted strings
	            if (tokid == token.NAME):
	                if tokval not in ['true', 'false', 'null', '-Infinity', 'Infinity', 'NaN']:
	                    tokid = token.STRING
	                    tokval = u'"%s"' % tokval

	            # fix single-quoted strings
	            elif (tokid == token.STRING):
	                if tokval.startswith ("'"):
	                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

	            # remove invalid commas
	            elif (tokid == token.OP) and ((tokval == '}') or (tokval == ']')):
	                if (len(result) > 0) and (result[-1][1] == ','):
	                    result.pop()

	            # fix single-quoted strings
	            elif (tokid == token.STRING):
	                if tokval.startswith ("'"):
	                    tokval = u'"%s"' % tokval[1:-1].replace ('"', '\\"')

	            result.append((tokid, tokval))

	        return tokenize.untokenize(result)


	def validate(self, item):
		try:
			return item.strip()
		except:
			return ''