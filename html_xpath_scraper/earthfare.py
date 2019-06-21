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

class EarthfareSpider(scrapy.Spider):
    name = 'earthfare'
    domain = 'https://www.earthfare.com'
    request_url = 'https://www.earthfare.com/stores'

    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver.exe")

    def start_requests(self):
        url = self.domain
        yield scrapy.Request(url=url, callback=self.parse_stores)
    
    def parse_stores(self, response):
        url = self.request_url
        self.driver.get(url)
        time.sleep(2)
        source = self.driver.page_source.encode("utf8")
        tree = etree.HTML(source)
        stores_list = tree.xpath('//div[@class="single_store_inner"]//div//div[@class="row"]')
        if stores_list:
            for store_li in stores_list:
                store_name = store_li.xpath('.//h4[@class="store-name"]/text()')[0]
                store_addr = store_li.xpath('.//p[@class="store-address"]/text()')[0].strip()
                addr_list = store_addr.split('\n')
                addr = addr_list[0].strip()
                store_addr = addr_list[1].strip()
                addr_list = store_addr.split(', ')
                city = addr_list[0]
                store_addr = addr_list[1]
                addr_list = store_addr.split(' ')
                state = addr_list[0]
                zip_code = addr_list[1]
                store_phone = store_li.xpath('.//div[@class="store-phone"]/text()')[0].strip()
                store_hour = store_li.xpath('.//div[@class="store-hours"]/text()')[0].strip()
                store_lat = store_li.xpath('.//div[@class="store-lat"]/text()')[0].strip()
                store_lng = store_li.xpath('.//div[@class="store-long"]/text()')[0].strip()

                item = ChainItem()
                item['store_name'] = store_name
                item['address'] = addr
                item['city'] = city
                item['state'] = state
                item['zip_code'] = zip_code
                item['phone_number'] = store_phone
                if store_hour:
                    item['store_hours'] = 'hours' + store_hour
                    item['coming_soon'] = '0'
                else:
                    item['coming_soon'] = '1'
                item['latitude'] = store_lat
                item['longitude'] = store_lng
                item['country'] = 'United States'

                yield item




        
    
    

    
        