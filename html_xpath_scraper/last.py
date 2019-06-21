# -*- coding: utf-8 -*-
import scrapy
import json
from ProjectReporter.items import ProjectreporterItem
import math
import pdb
from xlrd import open_workbook
from xlutils.copy import copy


class LastSpider(scrapy.Spider):

	name = 'last'
	allowed_domain = 'https://projectreporter.nih.gov/'

	start_url = 'https://projectreporter.nih.gov/reporter.cfm'
	email_url = 'https://projectreporter.nih.gov/VEmailReq.cfm'
	search_url = ''

	aid_calumn = 0
	pid_calumn = 30
	email_calumn = 10


	def __init__(self, *args, **kwargs):
		self.source = open_workbook('1.xlsx')
		self.dist = copy(self.source)
		self.s_sheet = self.source.sheets()[0]
		self.d_sheet = self.dist.get_sheet(0)


	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.startSearch)


	def startSearch(self, response):

		for row_num in range(self.s_sheet.nrows):
			if row_num > 0:
				row_valaues = self.s_sheet.row_values(row_num)
				aid_value = self.makeAID(row_valaues[self.aid_calumn])
				pid_value = self.makePID(row_valaues[self.pid_calumn])

				url =  self.email_url + "?aid=" + aid_value + "&pid=" + pid_value
				self.d_sheet.write(row_num, self.email_calumn, url)
				print "================== finished 1 row ==================="

		print "============== finished making url ======================"
		self.dist.save('result.xlsx')




	def makeAID(self, param):
		try:
			return str(param).replace('.0', '').strip()
		except:
			return ""


	def makePID(self, param):
		try:
			temp = ""
			flag = True
			for c in param:
				if c != ";" and flag == True:
					temp = temp + c
				else:
					flag = False
			return temp.replace('(contact)', '').strip()
		except:
			return ""



