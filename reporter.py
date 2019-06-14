# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException 
import json
from ProjectReporter.items import ProjectreporterItem
import math
import pdb
from xlrd import open_workbook
from xlutils.copy import copy
from time import sleep, time
from random import uniform, randint


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


def check_exists_by_xpath(driver, xpath):
		try:
				driver.find_element_by_xpath(xpath)
		except NoSuchElementException:
				return False
		return True
	
def wait_between(a,b):
	rand=uniform(a, b) 
	sleep(rand)

def dimention(driver): 
	d = int(driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table').get_attribute("class")[-1]);
	return d if d else 3  # dimention is 3 by default

def solve_images(driver):	
	WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.ID ,"rc-imageselect-target"))
				) 		
	dim = dimention(driver)	
	# ****************** check if there is a clicked tile ******************
	if check_exists_by_xpath(driver, '//div[@id="rc-imageselect-target"]/table/tbody/tr/td[@class="rc-imageselect-tileselected"]'):
		rand2 = 0
	else:  
		rand2 = 1 
	# wait before click on tiles 	
	wait_between(0.5, 1.0)		 
	# ****************** click on a tile ****************** 
	tile1 = WebDriverWait(driver, 10).until(
				EC.element_to_be_clickable((By.XPATH ,   '//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(randint(1, dim), randint(1, dim )))) 
		)   
	tile1.click() 
	if (rand2):
		try:
			driver.find_element_by_xpath('//div[@id="rc-imageselect-target"]/table/tbody/tr[{0}]/td[{1}]'.format(randint(1, dim), randint(1, dim))).click()
		except NoSuchElementException:          		
				print('\n\r No Such Element Exception for finding 2nd tile')
	#****************** click on submit buttion ****************** 
	driver.find_element_by_id("recaptcha-verify-button").click()
 



class ReporterSpider(scrapy.Spider):

	name = 'reporter'
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

				url =  self.email_url + "?aid=" + aid_value + "&pid=" + pid_value
				self.driver.get(url)
				if WebDriverWait(self.driver, 60).until(findIFrame):
					frame = self.driver.find_element_by_xpath('//iframe[contains(@src, "recaptcha")]')
					self.driver.switch_to.frame(frame)
					if WebDriverWait(self.driver, 60).until(findCheckBox):
						self.driver.find_element_by_xpath('//span[@id="recaptcha-anchor"]').click()
						self.driver.switch_to.default_content()
						wait_between(2.0, 2.5)

						self.driver.switch_to.frame(self.driver.find_elements_by_tag_name("iframe")[1])
						i=1
						while i<130:
							print('\n\r{0}-th loop'.format(i))
							# ******** check if checkbox is checked at the 1st frame ***********
							self.driver.switch_to.default_content()  
							WebDriverWait(self.driver, 10).until(
										EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME , 'iframe'))
										)  
							wait_between(1.0, 2.0)
							if check_exists_by_xpath(self.driver, '//span[@aria-checked="true"]'): 
								import winsound
								winsound.Beep(400,1500)
								break 
								
							self.driver.switch_to.default_content()  
							# ********** To the second frame to solve pictures *************
							wait_between(0.3, 1.5) 
							self.driver.switch_to_frame(self.driver.find_elements_by_tag_name("iframe")[1]) 
							solve_images(self.driver)
							i=i+1

						wait_between(0.3, 1.5)
						self.driver.switch_to.default_content()
						self.driver.find_element_by_xpath('//a[@title="Select"]').click()
						if WebDriverWait(self.driver, 60).until(findEmail):
							email = self.driver.find_element_by_xpath('//a[1]').text
							print "============== email ================"
							print email





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



