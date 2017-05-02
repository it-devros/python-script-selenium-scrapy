import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

class HarveysSpider(scrapy.Spider):
    name = 'harveys'
    domain = 'https://www.harveys.ca/eng/locations?province_val=bc&city_val=Vancouver&imageField.x=29&imageField.y=7'
    provinces = []
    cities = []

    def start_requests(self):
        url = self.domain
        yield scrapy.Request(url=url, callback=self.parse_home)

    def parse_home(self, response):
        scripts_eles = response.xpath('//script')
        if scripts_eles:
            for script_ele in scripts_eles:
                script_txt = script_ele.xpath('./text()').extract_first()
                print(script_txt)
                # if script_txt.find('location_map.php?id=') == 1:
                #     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                #     print(script_txt)
                #     print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                #     break
