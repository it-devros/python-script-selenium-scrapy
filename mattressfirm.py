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


class MattressfirmSpider(scrapy.Spider):
    name = 'mattressfirm'
    request_url = 'https://maps.mattressfirm.com/api/getAsyncLocations?template=searchmap&level=search&radius=500&lat=%s&lng=%s'
    states = []
    uid_list = []
    us_state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']

    def __init__(self):
        with open('states.json', 'r') as f:
            self.states = json.load(f)
        

    def start_requests(self):
        self.uid_list = []
        for state in self.states:
            url = self.request_url % (state['latitude'], state['longitude'])
            yield scrapy.Request(url=url, callback=self.parse_store)

    def parse_store(self, response):
        stores = json.loads(response.body)
        stores_list = []
        try:
            stores_list = stores['markers']
        except:
            print("+++++++++++++++++++++ no store lists")
        if stores_list:
            for store in stores_list:
                temp_lat = store['lat']
                temp_lng = store['lng']
                temp_locationID = store['locationId']
                if not temp_locationID in self.uid_list:
                    self.uid_list.append(temp_locationID)
                    temp_str = store['info']
                    temp_st = temp_str.split('href="')
                    temp_href_li = temp_st[1].split('"')
                    temp_href = temp_href_li[0]
                    request = scrapy.Request(url=temp_href, callback=self.parse_detail)
                    request.meta['lat'] = temp_lat
                    request.meta['lng'] = temp_lng
                    request.meta['locationID'] = temp_locationID
                    yield request
                else:
                    print("+++++++++++++++++++++++++++++ already scraped")
        else:
            print("++++++++++++++++++++ no store")

    def parse_detail(self,response):
        try:
            store_info = response.xpath('//div[@id="rls-tel-add"]')
        except:
            print("++++++++++++++++++++++++++++++ store detail does not exist")
        
        if store_info:
            for store in store_info:
                store_addr = store.xpath('.//div[@id="rls-address"]//span/text()').extract()
                temp_state = self.string_validate(store_addr[2])
                if temp_state in self.us_state_list:
                    item = ChainItem()
                    item['store_number'] = self.string_validate(response.meta['locationID'])
                    item['latitude'] = self.string_validate(response.meta['lat'])
                    item['longitude'] = self.string_validate(response.meta['lng'])
                    store_name = store.xpath('.//div[@class="rls-info-head"]//span[@class="rls-location-name"]/text()').extract_first()
                    item['store_name'] = self.string_validate(store_name.strip())

                    item['address'] = self.string_validate(store_addr[0])
                    item['address2'] = self.string_validate(store_addr[1])
                    item['state'] = self.string_validate(store_addr[2])
                    item['zip_code'] = self.string_validate(store_addr[3])

                    store_phone = store.xpath('.//div[@class="rio-store-phone"]//span/text()').extract_first()
                    item['phone_number'] = store_phone
                    try:
                        str_hours = ''
                        temp_store_hours = response.xpath('//div[@class="day-hour-row"]//meta[@itemprop="openingHours"]/@content').extract()
                        print(temp_store_hours)
                        for hour_li in temp_store_hours:
                            print(hour_li)
                            str_hours += hour_li + '; '
                        print(str_hours)
                        item['store_hours'] = str_hours
                    except:
                        item['store_hours'] = ''
                        print('++++++++++++++++++++++++++++++++ store hours empty')
                    
                    yield item
                else:
                    print('++++++++++++++++++++++++++++++ not US')
        else:
            print('+++++++++++++++++++ no detailed store info')        

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
    
