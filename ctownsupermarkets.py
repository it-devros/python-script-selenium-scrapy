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

class ctownsupermarkets(scrapy.Spider):
	name = 'ctownsupermarkets'
	domain = 'https://www.ctownsupermarkets.com'
	history = ['']

	def start_requests(self):
		payload = '<request><appkey>CD9028CC-DDFD-11DE-AECD-09680AC4B31A</appkey><geoip>1</geoip><formdata id="locatorsearch"><dataview>store_default</dataview><atleast>4</atleast><geolocs><geoloc><addressline>Enter address</addressline><longitude></longitude><latitude></latitude></geoloc></geolocs><searchradius>5|6|7|8|9|10|12|15|17|20|22|25|27|30|35|40|45|50|100|250|500|1000|2000|5000</searchradius></formdata></request>'
		yield scrapy.Request(url='https://hosted.where2getit.com/ctownmarket/ajax?&xml_request=%s' % payload, callback=self.body)

	def body(self, response):
		store_list = response.xpath('//collection//poi')
		for store in store_list:
			item = ChainItem()
			item['store_name'] = self.validate(store.xpath('.//name/text()'))
			item['store_number'] = self.validate(store.xpath('.//circular_id_publication/text()'))
			item['address'] = self.validate(store.xpath('.//address1/text()'))
			item['address2'] = self.validate(store.xpath('.//address2/text()'))
			item['phone_number'] = self.validate(store.xpath('.//phone/text()'))
			item['city'] = self.validate(store.xpath('.//city/text()'))
			item['state'] = self.validate(store.xpath('.//state/text()'))
			item['zip_code'] = self.validate(store.xpath('.//postalcode/text()'))
			item['country'] = self.validate(store.xpath('.//country/text()'))
			item['latitude'] = self.validate(store.xpath('.//latitude/text()'))
			item['longitude'] = self.validate(store.xpath('.//longitude/text()'))
			item['store_hours'] = 'Monday' + ' ' + self.validate(store.xpath('.//monopen/text()')) + '-' + self.validate(store.xpath('.//monclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//tueopen/text()')) + '-' + self.validate(store.xpath('.//tueclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//wedopen/text()')) + '-' + self.validate(store.xpath('.//wedclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//thuopen/text()')) + '-' + self.validate(store.xpath('.//thuclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//friopen/text()')) + '-' + self.validate(store.xpath('.//friclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//satopen/text()')) + '-' + self.validate(store.xpath('.//satclose/text()')) + ', '
			item['store_hours'] += 'Tuesday' + ' ' + self.validate(store.xpath('.//sunopen/text()')) + '-' + self.validate(store.xpath('.//sunclose/text()'))
			item['store_type'] = ''
			item['other_fields'] = ''
			item['coming_soon'] = ''
			yield item

	def validate(self, item):
		try:
			return item.extract_first().strip()
		except:
			return ''