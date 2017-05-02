import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import time
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


class PizzahutSpider(scrapy.Spider):
    name = 'pizzahut'
    request_url = 'https://www.pizzahut.com/#/find-a-hut'
    domain = 'https://www.pizzahut.com/'
    cities = []
    uid_list = []

    def __init__(self):
        with open('citiesusca.json', 'r') as f:
            self.cities = json.load(f)
        self.driver = webdriver.Chrome("./chromedriver.exe")
    
    def start_requests(self):
        url = self.domain
        self.driver.get(url)
        self.driver.find_element_by_link_text('Find a Pizza Hut').click()
        time.sleep(2)
        input_city = self.driver.find_element_by_name('City')
        input_city.send_keys(self.cities['Violet Hill']['city'])
        input_state = self.driver.find_element_by_name('State')
        input_state.send_keys('AR')
        self.driver.find_element_by_link_text('SEARCH').click()

        temp_state = 'NY'
        temp_city = 'New York'

        url = 'https://www.pizzahut.com/api.php/site/api_ajax/find_nearby'
        temp_param = temp_city + ',' + temp_state
        frmdata = {'occasion': 'C', 'zip': temp_param, 'near': temp_param, 'address': '', 'dine_in': 'false', 'mob_find': 'true', 'store_limit': '50' }
        str_frmdata = json.dumps(frmdata)
        yield FormRequest(url, callback=self.parse_response, formdata=frmdata)

    def parse_response(self, response):
        print(response)
