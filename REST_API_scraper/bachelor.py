# -*- coding: utf-8 -*-
import scrapy
import json
from Bachelor.items import BachelorItem
import math
import pdb


class BachelorSpider(scrapy.Spider):

	name = "bachelor"
	allowed_domain = 'https://www.bachelorsportal.com'

	detail_url = "https://www.bachelorsportal.com/studies/"
	api_url = "https://search.prtl.co/2018-07-23/"

	def start_requests(self):
		index = 0
		while index < 2440:
			url =  self.api_url + "?start=" + str(index) + "&q=di-6%7Cen-2876%7Clv-bachelor%2Cpreparation%7Ctc-EUR%7Cuc-11%7Cur-38"
			yield scrapy.Request(url=url, callback=self.parseList)
			index += 10


	def parseList(self, response):
		bachelorList = json.loads(response.body)
		for bachelor in bachelorList:
			url = self.detail_url + str(bachelor['id'])

			degree_type = ""
			try:
				degree_type = bachelor['degree']
			except:
				degree_type = ""

			name = ""
			try:
				name = bachelor['title']
			except:
				name = ""

			university = ""
			try:
				university = bachelor['organisation']
			except:
				university = ""

			log = ""
			try:
				log = bachelor['logo']
			except:
				log = ""

			summary = ""
			try:
				summary = bachelor['summary']
			except:
				summary = ""

			location = ""
			country = ""
			try:
				for loc in bachelor['venues']:
					location += loc['city'] + ", " + loc['area'] + ", " + loc['country'] + " | "
					country += loc['country'] + " | "
				location = location[:-3]
				country = country[:-3]
			except:
				location = ""

			attendance = ''
			duration = ""
			try:
				density = bachelor['density']
			except:
				density = False

			if density and density['fulltime']:
				attendance = "Full-time"
				try:
					duration = str(bachelor['fulltime_duration']['value']) + " " + bachelor['fulltime_duration']['unit']
				except:
					duration = ""
			elif density and density['parttime']:
				attendance = "Part-time"
				try:
					duration = str(bachelor['parttime_duration']['value']) + " " + bachelor['parttime_duration']['unit']
				except:
					duration = ""

			try:
				tuition = str(bachelor['tuition_fee']['value'])	 + bachelor['tuition_fee']['currency'] + "/" + bachelor['tuition_fee']['unit']
			except:
				tuition = ""

			param = {
				"degree_type": degree_type,
				"name": name,
				"university": university,
				"location": location,
				"attendance": attendance,
				"duration": duration,
				"tuition": tuition,
				"log": log,
				"country": country,
				"small_desc": summary
			}
			yield scrapy.Request(url=url, callback=self.parseDetail, meta=param)


	def parseDetail(self, response):
		item = BachelorItem()
		item['degree_type'] = self.validateStr(response.meta['degree_type'])
		item['name'] = self.validateStr(response.meta['name'])
		item['university'] = self.validateStr(response.meta['university'])
		item['location'] = self.validateStr(response.meta['location'])
		item['attendance'] = self.validateStr(response.meta['attendance'])

		deadline = ""
		deadlines = self.eliminateTextList(response.xpath('//li[@class="ApplicationDeadlines"]/time/text()').extract())
		for dead in deadlines:
			deadline += dead + " "
		if deadline == "":
			deadline = self.validateStr(response.xpath('//span[@class="QFDetails"]/div/span/text()').extract_first())
		if deadline == False:
			deadline = self.validateStr(response.xpath('//span[@class="QFDetails"]/div/text()').extract_first())
		item['application_deadline'] = deadline

		item['duration'] = self.validateStr(response.meta['duration'])
		item['tuition'] = self.validateStr(response.meta['tuition'])
		item['log'] = self.validateStr(response.meta['log'])
		item['country'] = self.validateStr(response.meta['country'])
		item['small_desc'] = self.validateStr(response.meta['small_desc'])

		item['long_desc'] = self.validateStr(response.xpath('//section[@id="StudyDescription"]').extract_first())
		item['programme_structue'] = self.validateStr(response.xpath('//article[@id="StudyContents"]').extract_first())
		item['key_facts'] = self.validateStr(response.xpath('//section[@id="StudyKeyFacts"]').extract_first())
		item['language'] = self.validateStr(response.xpath('//section[@id="StudyKeyFacts"]//div[@class="Languages"]//ul[@class="FactData"]//li/text()').extract_first())


		keyList = response.xpath('//section[@id="StudyKeyFacts"]//li[@class="FactItem"]')
		for li in keyList:
			title = self.validateStr(li.xpath('.//span[@class="FactItemLabel"]/text()').extract_first())
			if title == 'Delivery mode':
				item['delivery_mode'] = self.validateStr(li.xpath('.//div[@class="FactData"]/text()').extract_first())

		item['academic_requirements'] = self.validateStr(response.xpath('//section[@id="AcademicRequirements"]').extract_first())

		yield item
		



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



