<<<<<<< HEAD
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

class LazboySpider(scrapy.Spider):
    name = "lazboy"
    request_url = "http://www.la-z-boy.com/storeLocator/storeLocator.jsp"
    domain ='http://www.la-z-boy.com/'
    us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
    canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
    zip_lines = []
    uid_list = []

    def __init__(self):
        with open('citiesusca.json', 'r') as f:
            self.zip_lines = json.load(f)
        self.driver = webdriver.Chrome("./chromedriver.exe")
        
    
    def start_requests(self):
        url = self.domain
        yield scrapy.Request(url=url, callback=self.parse_state)

    def parse_state(self, response):
        url = self.request_url
        for zip_line in self.zip_lines:
            self.driver.get(url)
            time.sleep(1)
            line = self.zip_lines[zip_line]['city']
            
            zip_input = self.driver.find_element_by_name("locator")
            zip_input.send_keys('')
            zip_input.send_keys(line)
            self.driver.find_element_by_id("findStore").click()
            time.sleep(1)
            source = self.driver.page_source.encode("utf8")
            tree = etree.HTML(source)

            store_list =[]
            try:
                store_list = tree.xpath('//div[@id="storeResultsContainer"]//div[@class="stores-tab"]')
            except:
                print("++++++++++++++++++++++++++ no stores in this zip code")

            if store_list:
                i = 0
                for store_li in store_list:
                    
                    store_info = self.validate(store_li.xpath('.//p/text()'))
                    zip_country = self.string_validate(store_info[2].strip())
                    temp_zip_country = self.validate(zip_country.split(', '))
                    temp_zip_code = self.string_validate(temp_zip_country[0])

                    if temp_zip_code:
                        if not temp_zip_code in self.uid_list:
                            self.uid_list.append(temp_zip_code)
                            item = ChainItem()
                            store_name_temp = self.validate(store_li.xpath('.//h4/text()'))
                            item['store_name'] = self.string_validate(store_name_temp[0].strip())
                            item['address'] = self.string_validate(store_info[0].strip())

                            city_state = self.string_validate(store_info[1].strip())
                            temp_city_state = self.validate(city_state.split(', '))
                            item['city'] = self.string_validate(temp_city_state[0])
                            item['state'] = self.string_validate(temp_city_state[1])

                            item['zip_code'] = temp_zip_code
                            if self.count_validate(temp_zip_country) > 0:
                                temp_country = self.string_validate(temp_zip_country[1])
                                if temp_country == 'US':
                                    item['country'] = 'United States'
                            try:
                                self.driver.find_element_by_xpath('//span[@class="btn-secondary more_info"][@data-index="' + str(i) + '"]').click()
                                i = i + 1
                                source = self.driver.page_source.encode("utf8")
                                tree = etree.HTML(source)
                                
                                temp_phone = tree.xpath('//a[@class="info-phone-dialog info-dialog-data"]/text()')
                                item['phone_number'] = temp_phone[0]
                            except:
                                item['phone_number'] = 'None'
                                i = i + 1
                                source = self.driver.page_source.encode("utf8")
                                tree = etree.HTML(source)

                            yield item
                        else:
                            print("++++++++++++++++++++++++++++++++++++ already scraped")
                    else:
                        print("++++++++++++++++++++++++++++++++++ it does not exist")
            


    def validate(self, some_list):
        try:
            if some_list:
                return some_list
        except:
            print("++++++++++++++++++++++++++++++++++value error. I can't get the DOM")
            temp_list = ['None', 'None']
            return temp_list

    def string_validate(self, some_string):
        try:
            if some_string:
                return some_string
        except:
            print("++++++++++++++++++++++++++++++++++ string is empty")
            temp_string = 'None'
            return temp_string

    def count_validate(self, some_list):
        if some_list:
            i = 0
            for one_li in some_list:
                i = i + 1
            return i
        else:
            return 0
=======
import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class LazboySpider(scrapy.Spider):
    name = "lazboy"
    search_url = "http://www3.samsclub.com/clublocator/statelisting.aspx?mySearch=state&myState="

    start_urls = ["http://www3.samsclub.com/clublocator/",]
 
    def parse(self, response):
        states = response.xpath("//select[@id='ctl00_MainContent_ddlState']/option/text()").extract()
        for state in states:
            if state.strip() == "":
                continue
            yield scrapy.Request(url=self.search_url+state, callback=self.parse_stores)

    def parse_stores(self, response):
        body = response.body
        try:
            json_str = body.split(";plotClubs(")[1].split(",true, null")[0].strip()
            json_str = '[{"Address1"' + json_str.split(',[{"Address1"')[1]
        except:
            return

        stores = json.loads(json_str)
        for store in stores:
            item = ChainItem()
            item['store_name'] = store["ClubName"]
            item['store_number'] = store["ClubNumber"]
            item['address'] = store["Address1"]
            item['address2'] = store["Address2"] if store["Address2"] != None else ""
            item['phone_number'] = store["PhoneNumber"]
            item['city'] = store["City"]
            item['state'] = store["State"]
            item['zip_code'] = store["PostalCode"]
            item['country'] = "United States"
            item['latitude'] = store["Latitude"]
            item['longitude'] = store["Longitude"]
            item['store_hours'] = []
            for hr in store["Schedule"]:
                item['store_hours'].append("%s: %s" % (hr["Type"], hr["Summary"].replace("\n", "; ")))
            item['store_hours'] = "; ".join(item['store_hours']).strip()

            #item['store_type'] = info_json["@type"]
            item['other_fields'] = ""
            item['coming_soon'] = "0"
            yield item



>>>>>>> ff363424058f39a36f4e98c07350af5fadbfe4b9
