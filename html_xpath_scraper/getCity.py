# -*- coding: utf-8 -*-
import scrapy
import json
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from TripAdvisor.items import CityItem
import time
import pdb


class GetCitySpider(scrapy.Spider):
	name = 'getCity'
	allowed_url = 'https://www.tripadvisor.com'

	# start_url = 'https://www.tripadvisor.com/Attractions-g21-Activities-Middle_East.html'			# Middle East
	# start_url = 'https://www.tripadvisor.com/Attractions-g4-Activities-Europe.html'			# Europe
	# start_url = 'https://www.tripadvisor.com/Attractions-g2-Activities-Asia.html'			# Asia
	# start_url = 'https://www.tripadvisor.com/Attractions-g291958-Activities-Central_America.html'			# Central America
	# start_url = 'https://www.tripadvisor.com/Attractions-g6-Activities-Africa.html'			# Africa
	# start_url = 'https://www.tripadvisor.com/Attractions-g8-Activities-South_Pacific.html'			# South Pacific
	# start_url = 'https://www.tripadvisor.com/Attractions-g13-Activities-South_America.html'			# South America

	# start_url = 'https://www.tripadvisor.com/Attractions-g153339-Activities-Canada.html' 		# Canada
	# start_url = 'https://www.tripadvisor.com/Attractions-g191-Activities-United_States.html' 		# United States
	# start_url = 'https://www.tripadvisor.com/Attractions-g147237-Activities-Caribbean.html' 	# Caribbean
	start_url = 'https://www.tripadvisor.com/Attractions-g150768-Activities-Mexico.html' 	# Mexico


	def __init__(self):
		options = webdriver.ChromeOptions()
		options.add_argument("--start-maximized")
		self.driver = webdriver.Chrome("./chromedriver", chrome_options=options)


	def start_requests(self):
		url = self.start_url
		yield scrapy.Request(url=url, callback=self.startSelenium)


	def startSelenium(self, response):
		url = self.start_url
		self.driver.get(url)
		time.sleep(1)

		# locations = self.driver.find_elements_by_xpath("//div[@class='geo_image']/a")
		# for location in locations:
		# 	temp = location.get_attribute("href")
		# 	item = CityItem()
		# 	item['url'] = self.allowed_url + temp
		# 	yield item
		# self.driver.find_element_by_xpath("//a[@data-page-number='2']").click()

		# locations = self.driver.find_elements_by_xpath("//ul[@class='geoList']//li//a")
		# for location in locations:
		# 	temp = location.get_attribute("href")
		# 	item = CityItem()
		# 	item['url'] = self.allowed_url + temp
		# 	yield item

		# nextLinks = self.driver.find_elements_by_xpath("//div[@class='pgLinks']//a")
		# while len(nextLinks) >= 10:
		# 	if len(nextLinks) == 10:
		# 		nextLinks[4].click()
		# 	if len(nextLinks) > 10:
		# 		nextLinks[5].click()
		# 	locations = self.driver.find_elements_by_xpath("//ul[@class='geoList']//li//a")
		# 	for location in locations:
		# 		temp = location.get_attribute("href")
		# 		item = CityItem()
		# 		item['url'] = self.allowed_url + temp
		# 		yield item
		# 	nextLinks = self.driver.find_elements_by_xpath("//div[@class='pgLinks']//a")





		citys = self.driver.find_elements_by_xpath("//div[@class='navigation_list']")
		locations = citys[1].find_elements_by_xpath(".//div[@class='ap_navigator']/a")
		flag = 0
		element = {}
		for location in locations:
			temp = location.get_attribute("href")
			if location.text != 'More':
				item = CityItem()
				item['url'] = self.allowed_url + temp
				yield item
			else:
				flag = 1
				element = location

		if flag == 1:
			element.click()
			time.sleep(1)
			locations = self.driver.find_elements_by_xpath("//ul[@class='geoList']//li//a")
			for location in locations:
				temp = location.get_attribute("href")
				item = CityItem()
				item['url'] = self.allowed_url + temp
				yield item

			nextLinks = self.driver.find_elements_by_xpath("//div[@class='pgLinks']//a")
			while len(nextLinks) >= 10:
				if len(nextLinks) == 10:
					nextLinks[4].click()
				if len(nextLinks) > 10:
					nextLinks[5].click()
				locations = self.driver.find_elements_by_xpath("//ul[@class='geoList']//li//a")
				for location in locations:
					temp = location.get_attribute("href")
					item = CityItem()
					item['url'] = self.allowed_url + temp
					yield item
				nextLinks = self.driver.find_elements_by_xpath("//div[@class='pgLinks']//a")


