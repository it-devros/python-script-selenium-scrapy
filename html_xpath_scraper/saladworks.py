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

class SaladworksSpider(scrapy.Spider):
    name = 'saladworks'
    domain = 'www.saladworks.com'
    request_url = 'https://online.saladworks.com/#/selectlocation'
    places = []
    us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
    uid_list = []

    def __init__(self):
        with open('saladworks.json', 'r') as f:
            self.places = json.load(f)
        self.driver = webdriver.Chrome("./chromedriver.exe")

    def start_requests(self):
        url = self.request_url
        # print self.places['Regions'][0]['Name']
        # print self.places['Regions'][0]['Districts'][0]['DistrictName']
        # frmdata = {'Region': self.places['Regions'][0]['Name'], 'District': self.places['Regions'][0]['Districts'][0]['DistrictName'], 'Zipcode': ''}
        # yield scrapy.Request(url=url, method='PUT', body=json.dumps(frmdata), callback=self.parse_keys)
        yield scrapy.Request(url=url, callback=self.parse_stores)

    def parse_stores(self, response):
        url = self.request_url
        self.driver.get(url)
        time.sleep(2)

        for place in self.places['Regions']:
            if place['Name'] in self.us_state_list:
                state_key = self.driver.find_element_by_name('state')
                state_key.send_keys('')
                state_key.send_keys(place['Name'])
                for place_city in place['Districts']:
                    city_key = self.driver.find_element_by_name('city')
                    city_key.send_keys('')
                    city_key.send_keys(place_city['DistrictName'])
                    btn_search = self.driver.find_element_by_link_text('Search')
                    btn_search.click()
                    time.sleep(2)

                    source = self.driver.page_source.encode("utf8")
                    tree = etree.HTML(source)

                    stores = tree.xpath('//div[@class="addressContent"]')
                    if stores:
                        for store in stores:
                            store_name = store.xpath('./strong/text()')[0].strip()
                            state = place['Name']
                            city = place_city['DistrictName']
                            store_info = store.xpath('.//span/text()')
                            address = store_info[2]
                            phone = store_info[4]
                            hours =store_info[5][12:]
                            addr_list = store_info[3].split(' ')
                            i = 0
                            for addr in addr_list:
                                i += 1
                            pc = addr_list[i - 1]
                            if not phone in self.uid_list:
                                self.uid_list.append(phone)
                                item = ChainItem()
                                item['store_name'] = store_name
                                item['address'] = address
                                item['city'] = city
                                item['state'] = state
                                item['phone_number'] = phone
                                item['zip_code'] = pc
                                item['store_hours'] = hours
                                item['coming_soon'] = '0'
                                item['country'] = 'United States'
                                yield item
                    else:
                        print('++++++++++++++++++++++++++++++++ no stores')
                        url = self.request_url
                        self.driver.get(url)
                        time.sleep(2)
