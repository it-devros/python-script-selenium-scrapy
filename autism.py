# -*- coding: utf-8 -*-
import scrapy
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Autism.items import UrlItem
import time
import datetime
import pdb


def findCountries(driver):
	elements = driver.find_elements_by_xpath('//select[@id="country"]//option')
	if elements:
			return True
	else:
			return False

def findItems(driver):
	elements = driver.find_elements_by_xpath('//section[@class="search"]//div[@class="search-details-main"]//div[@class="search-more"]/a')
	if elements:
			return True
	else:
			return False


class autismSpider(scrapy.Spider):

	name = 'autism'
	root_url = 'https://www.autismconnect.com'
	allowed_domain = 'https://www.autismconnect.com/directory/'
	start_url = 'https://www.autismconnect.com/directory/'


	def __init__(self):
		chromeOptions = Options()
		chromeOptions.add_argument("--start-maximized")
		self.driver = webdriver.Chrome("./chromedriver", chrome_options=chromeOptions)


	def start_requests(self):
		url = self.allowed_domain
		yield scrapy.Request(url=url, callback=self.startSelenium)


	def startSelenium(self, response):
		self.driver.get(self.start_url)
		WebDriverWait(self.driver, 10).until(findCountries)
		self.driver.find_element_by_xpath('//select[@id="country"]/option[@value="USA"]').click()
		self.driver.find_element_by_xpath('//div[@class="form-group-btn"]/button[@type="submit"]').click()


		loops = True
		index = 10
		while loops != False:
			time.sleep(5)
			pageList = self.driver.find_elements_by_xpath('//ul[@class="pagination"]/li')
			nextButton = False
			for page in pageList:
				try:
					label = self.validateStr(page.find_element_by_xpath('./a').text)
					if label == '87':
						loops = False
						nextButton = page
					if label == str(index) and loops:
							nextButton = page
							index += 4
				except:
					pass
			if nextButton:
				time.sleep(5)
				nextButton.click()

		flag = True

		while flag != False:
			WebDriverWait(self.driver, 10).until(findItems)
			time.sleep(5)
			details = self.driver.find_elements_by_xpath('//section[@class="search"]//div[@class="search-details-main"]//div[@class="search-more"]/a')
			for detail in details:
				url = self.validateStr(detail.get_attribute('href'))
				item = UrlItem()
				item['url'] = url
				yield item

			pageList = self.driver.find_elements_by_xpath('//ul[@class="pagination"]/li')
			nextButton = False
			for page in pageList:
				try:
					label = self.validateStr(page.find_element_by_xpath('./a').text)
					if label == 'Next':
						className = page.get_attribute('class')
						if className == 'disabled':
							flag = False
						else:
							nextButton = page
				except:
					pass
			if nextButton:
				time.sleep(5)
				nextButton.click()





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



