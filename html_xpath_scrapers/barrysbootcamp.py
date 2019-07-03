import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
from geopy.geocoders import Nominatim

class BarrysbootcampSpider(scrapy.Spider):
	name = 'barrysbootcamp'
	domain = 'https://www.barrysbootcamp.com'
	start_url = 'https://www.barrysbootcamp.com/site-map/'
	geolocator = Nominatim()

	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.parse_links)

	def parse_links(self, response):
		if response:
			store_links = response.xpath('//div[@class="page-group-column studio"]//ul[@class="nav flex-column"]//li//a/@href').extract()
			if store_links:
				for lin in store_links:
					yield scrapy.Request(url=lin, callback=self.parse_stores)
			else:
				print('++++++++++++++++++++++++++++++++ no store links')
		else:
			print('+++++++++++++++++++++++++++++++++ no response')

    def parse_stores(self, response):
			if response:
				content = response.xpath('//div[@class="info-wrap"]//div[@class="row"]//div[@class="column--2 address"]')
				if content:
					store_info = response.xpath('//div[@class="info-wrap"]//div[@class="row"]//div[@class="column--2 address"]//div[@id="studio-info"]')
					address = store_info.xpath('./div//dl//dd//div[@itemprop="address"]//span[@itemprop="streetAddress"]/text()').extract_first()
					city = store_info.xpath('./div//dl//dd//div[@itemprop="address"]//span[@itemprop="addressLocality"]/text()').extract_first()
					state = store_info.xpath('./div//dl//dd//div[@itemprop="address"]//span[@itemprop="addressRegion"]/text()').extract_first()
					zc = store_info.xpath('./div//dl//dd//div[@itemprop="address"]//span[@itemprop="postalCode"]/text()').extract_first()
					phone = store_info.xpath('./div//dl[@class="email-phone"]//dd//span[@itemprop="telephone"]/text()').extract_first()

					store_hours = response.xpath('//div[@class="info-wrap"]//div[@class="row"]//div[@class="column--2 address"]//div[@class="opening-hours-container"]')
					hours = store_hours.xpath('./dl[@class="opening-hours"]//dd[@class="dd--hours"]//meta[@itemprop="openingHours"]//@content').extract()
					store_hour = ''
					for hour in hours:
							store_hour += hour.strip() + '; '
					store_name = response.xpath('//header[@class="header"]//h1/@data-base-title').extract_first()


					_response = response.body
					response_list = _response.split('"locations":[')
					_response = response_list[1]
					response_list = _response.split('],"useClusters":"0"};')
					_response = response_list[0]
						
						
					store_li = _response.split('"name":"'+store_name+'"')
					_response = store_li[0]
					temp_list = _response.split('},{')
					i = 0
					for temp in temp_list:
							i += 1
					_response = temp_list[i - 1]

					store_li = _response.split('"lat":')
					_response = store_li[1]
					temp_list = _response.split(',')
					latitude = temp_list[0]
					
					store_li = _response.split('"lng":')
					_response = store_li[1]
					temp_list = _response.split(',')
					longitude = temp_list[0]

					store_li = _response.split('"id":')
					_response = store_li[1]
					temp_list = _response.split(',')
					store_id = temp_list[0]

					item = ChainItem()
					if store_name:
						item['store_name'] = store_name.strip()
					if address:
						item['address'] = address.strip()
					if city:
						item['city'] = city.strip()
					if state:
						item['state'] = state.strip()
					else:
						location = self.geolocator.reverse("%s, %s" % (latitude, longitude))
						item['state'] = location.raw["address"]["state"] if "state" in location.raw["address"] else ""
					if zc:
						item['zip_code'] = zc.strip()
					if phone:
						item['phone_number'] = phone
					if store_hour:
						item['store_hours'] = store_hour.strip()
					else:
						item['store_hours'] = ''
					if latitude:
						item['latitude'] = latitude.strip()
					if longitude:
						item['longitude'] = longitude.strip()
					if store_id:
						item['store_number'] = store_id.strip()
					item['country'] = 'United States'
					if item['city'] == 'London':
						item['country'] = 'United Kingdom'
					if item['city'] == 'Bergen':
						item['country'] = 'Norway'
					if item['city'] == 'Bergen':
						item['country'] = 'Norway'
					if item['city'].find('DIFC') != -1:
						item['country'] = 'Dubai'
					if item['city'] == 'Oslo':
						item['country'] = 'Norway'
					if item['city'] == 'Milan':
						item['country'] = 'Italy'
					if item['city'] == 'Fana':
						item['country'] = 'Norway'
					if item['city'] == 'Sandvika':
						item['country'] = 'Norway'


					if item['store_hours'] != '':
						item['coming_soon'] = '0'
					else:
						item['coming_soon'] = '1'

					yield item
							
				else:
					print('+++++++++++++++++++++++++++++++++++++++ no store detail')
			else:
					print('+++++++++++++++++++++++++++++++++ no responses')