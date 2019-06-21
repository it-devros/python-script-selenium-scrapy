# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from ProjectReporter.items import ProjectreporterItem
import math
import pdb
from xlrd import open_workbook
from xlutils.copy import copy
import time


def findSubmitQueryButton(driver):
	elements = driver.find_elements_by_xpath('//div[@class="rep_forms_button_qf"]//a[@title="Submit Query"]')
	if elements:
			return elements
	else:
			return False

def findElementList(driver):
	elements = driver.find_elements_by_xpath('//table[@id="main-table"]/tbody/tr[2]//a')
	if len(elements) >= 2:
		return elements
	else:
		return False

def findEmailButton(driver):
	elements = driver.find_elements_by_xpath('//a[@class="link6"]')
	if len(elements) > 0:
		return elements
	else:
		return False

def findIFrame(driver):
	frame = driver.find_element_by_xpath('//iframe[contains(@src, "recaptcha")]')
	if frame:
		return frame
	else:
		return False

def findCheckBox(driver):
	element = driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]')
	if element:
			return element
	else:
			return False

def findEmail(driver):
	elements = driver.find_elements_by_xpath('//span/a')
	if len(elements) > 0:
		return elements
	else:
		return False



class ProjectReporterSpider(scrapy.Spider):

	name = 'projectreporter'
	allowed_domain = 'https://projectreporter.nih.gov/'

	start_url = 'https://projectreporter.nih.gov/reporter.cfm'
	search_url = ''

	aid_calumn = 0
	pid_calumn = 30
	email_calumn = 10


	def __init__(self, *args, **kwargs):
		self.source = open_workbook('1.xlsx')
		self.dist = copy(self.source)
		self.s_sheet = self.source.sheets()[0]
		self.d_sheet = self.dist.get_sheet(0)

		chromeOptions = Options()
		chromeOptions.add_argument("--start-maximized")
		self.driver = webdriver.Chrome("./chromedriver", chrome_options=chromeOptions)	


	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.startSearch)


	def startSearch(self, response):
		for row_num in range(self.s_sheet.nrows):
			if row_num > 0 and row_num <= 4:
				row_valaues = self.s_sheet.row_values(row_num)
				aid_value = self.makeAID(row_valaues[self.aid_calumn])
				pid_value = self.makePID(row_valaues[self.pid_calumn])

				self.driver.get(self.start_url)
				WebDriverWait(self.driver, 60).until(findSubmitQueryButton)
				self.driver.find_element_by_id("p_projectnum").send_keys(aid_value)
				self.driver.find_element_by_xpath('//div[@class="rep_forms_button_qf"]//a[@title="Submit Query"]').click()
				
				if WebDriverWait(self.driver, 60).until(findElementList):
					self.driver.find_element_by_xpath('//table[@id="main-table"]/tbody/tr[2]//a[1]').click()
					if WebDriverWait(self.driver, 60).until(findEmailButton):
						newUrl = self.allowed_domain + "VEmailReq.cfm?aid=" + aid_value + "&pid=" + pid_value
						self.driver.get(newUrl)

						if WebDriverWait(self.driver, 60).until(findIFrame):
							frame = self.driver.find_element_by_xpath('//iframe[contains(@src, "recaptcha")]')
							self.driver.switch_to.frame(frame)
							if WebDriverWait(self.driver, 60).until(findCheckBox):
								self.driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]').click()
								self.driver.switch_to.default_content()

								if WebDriverWait(self.driver, 300).until(findEmail):
									email = self.driver.find_element_by_xpath('//a[1]').text
									print "============== email ================"
									print email
					else:
						print "================ no email button ================="
						pass
				else:
					print "================= no result ===================="
					pass





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



