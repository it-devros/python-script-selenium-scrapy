# -*- coding: utf-8 -*-
import scrapy
import json
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from MiamiDade.items import MiamidadeItem
import time
import datetime
import pdb


def findAuctionList(driver):
	elements = driver.find_elements_by_xpath('//div[@id="Area_C"]/div[@tabindex="0"]')
	if elements:
			return elements
	else:
			return False


def findPageNation(driver):
	element = driver.find_element_by_id('maxCA')
	if element and element.text:
			return element
	else:
			return False


class MiamiDadeSpider(scrapy.Spider):

	name = 'miamidade'
	allowed_domain = 'https://www.miamidade.realforeclose.com'

	root_url = "https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&zmethod=PREVIEW&AuctionDate="

	def __init__(self):
		chromeOptions = Options()
		chromeOptions.add_argument("--start-maximized")
		self.driver = webdriver.Chrome("./chromedriver", chrome_options=chromeOptions)


	def start_requests(self):
		url = self.allowed_domain
		yield scrapy.Request(url=url, callback=self.startSelenium)


	def startSelenium(self, response):


		cursorDate = datetime.datetime(2018, 3, 1)
		lastDate = datetime.datetime(2018, 9, 1)

		while cursorDate < lastDate:
			param = str(cursorDate.month) + "/" + str(cursorDate.day) + "/" + str(cursorDate.year)
			url = self.root_url + param
			self.driver.get(url)

			index = 1
			try:
				pageNation = WebDriverWait(self.driver, 5).until(findPageNation)
				length = self.validateStr(pageNation.text)
				length = int(length)
			except:
				length = 0

			print "++++++++++++++++++++++++"
			print length

			while index <= length:
				auctionList = []
				try:
					WebDriverWait(self.driver, 60).until(findAuctionList)
					time.sleep(5)
					auctionList = self.driver.find_elements_by_xpath('//div[@id="Area_C"]/div[@tabindex="0"]')
				except:
					auctionList = []

				for auction in auctionList:
					details = auction.find_elements_by_xpath('./div/table[@class="ad_tab"]/tbody/tr')
					item = MiamidadeItem()
					is_realfore = False
					for detail in details:
						title = self.validateStr(detail.find_element_by_xpath('./th').text)
						if title == "Auction Type:":
							value = self.validateStr(detail.find_element_by_xpath('./td').text)
							if value == "FORECLOSURE":
								is_realfore = True
								item['auction_type'] = value

						if is_realfore == True:
							value = self.validateStr(detail.find_element_by_xpath('./td').text)
							if title == "Case #:":
								item['case_sharpe'] = value

							if title == "Final Judgment Amount:":
								item['judgement_amount'] = value

							if title == "Parcel ID:":
								temp = self.validateStr(detail.find_element_by_xpath('./td/a').text)
								item['parcel_id'] = temp
								item['url'] = self.validateStr(detail.find_element_by_xpath('./td/a').get_attribute('href'))

							if title == "Property Address:":
								item['proprty_address_1'] = value

							if title == "":
								tempList = value.split(",")
								if len(tempList) > 1:
									item['city'] = tempList[0]
									item['zipcode'] = tempList[1]
								else:
									item['city'] = tempList[0]

							if title == "Assessed Value:":
								item['assessed_value'] = value

							if title == "Plaintiff max bid:":
								item['plaintiff_max_bid'] = value

					if is_realfore == True:
						title = self.validateStr(auction.find_element_by_xpath('./div[@class="AUCTION_STATS"]/div[1]').text)
						if title == "Auction Sold":
							datetimeStr = self.validateStr(auction.find_element_by_xpath('./div[@class="AUCTION_STATS"]/div[2]').text)
							datetimeList = self.eliminateTextList(datetimeStr.split(" "))
							try:
								item['date'] = datetimeList[0]
								item['time'] = self.validateStr(datetimeStr.replace(datetimeList[0], ""))
							except:
								pass
							item['amount'] = self.validateStr(auction.find_element_by_xpath('./div[@class="AUCTION_STATS"]/div[4]').text)
							item['sold_to'] = self.validateStr(auction.find_element_by_xpath('./div[@class="AUCTION_STATS"]/div[6]').text)
						yield item


				index += 1
				self.driver.find_element_by_xpath('//div[@class="Head_C"]/div[@class="PageFrame"]/span[@class="PageRight"]').click()


			cursorDate += datetime.timedelta(days=1)



	
	

	def now_milliseconds(self):
		return int(time.time() * 1000)


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