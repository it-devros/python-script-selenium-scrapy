import scrapy, time
import selenium
from selenium import webdriver
from lxml import etree
import os
import json

class Tjmspider(scrapy.Spider):
    name = "tjmspider"
    item = {}    

    def __init__(self):
        self.driver = webdriver.Chrome("./chromedriver")
        self.index = 0

    def start_requests(self):
        init_url  = 'http://tjmaxx.tjx.com'
        header = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-US,en;q=0.8',
        'Cache-Control':'max-age=0',
        'Connection':'keep-alive',
        'Host':'tjmaxx.tjx.com',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
        }
        yield scrapy.Request(url=init_url, method='GET', headers=header, callback=self.parse)    
        
    def parse(self,response):       

        script_dir = os.path.dirname(__file__)
        file_path = script_dir + '/geo/cities.json'
        with open(file_path) as data_file:    
            location_list = json.load(data_file)
        for location in location_list: 
            self.driver.get("http://tjmaxx.tjx.com/store/stores/storeLocator.jsp?")  
            if self.index == 0:
                self.driver.find_element_by_id("modal-close").click()
            self.index = self.index + 1                                
            city = self.driver.find_element_by_id("store-location-city")
            state = self.driver.find_element_by_id("store-location-state")
            city.send_keys(location['city'])
            state.send_keys(location['state'])
            if self.driver.find_element_by_name("submit") is not None:
                self.driver.find_element_by_name("submit").click()
            source = self.driver.page_source.encode("utf8")
            tree = etree.HTML(source)
            store_list = tree.xpath('//li[@class="store-list-item vcard address"]')
            for store in store_list:
                self.item['store_name'] = store.xpath('.//h3/text()')[0].strip()
                self.item['store_number'] = ''
                self.item['address'] = store.xpath('.//div[@class="adr"]//span[@class="street-address"]/text()')[0].strip()
                self.item['address2'] = ''
                self.item['city'] = store.xpath('.//div[@class="adr"]//span[@class="locality"]/text()')[0].strip()
                self.item['state'] = store.xpath('.//div[@class="adr"]//abbr[@class="region"]/text()')[0].strip()
                self.item['zip_code'] = store.xpath('.//div[@class="adr"]//span[@class="postal-code"]/text()')[0].strip()
                self.item['country'] = 'United States'
                self.item['phone_number'] = store.xpath('.//div[@class="tel"]/text()')[0].strip()
                self.item['latitude'] = ''
                self.item['longitude'] = ''
                self.item['store_hours'] = store.xpath('.//time/text()')[0].strip()
                self.item['store_type'] = ''
                self.item['other_fields'] = ''
                self.item['distributor_name'] = ''
                yield self.item





        btn_next_disable = response.xpath('//a[@id="ctl00_PageContent_lbtnNext", @disabled="disabled"]')
        if not btn_next_disable:
            self.driver.find_element_by_id("ctl00_PageContent_lbtnNext").click()
            source = self.driver.page_source.encode("utf8")
            response = etree.HTML(source)
            self.parse_store(response)