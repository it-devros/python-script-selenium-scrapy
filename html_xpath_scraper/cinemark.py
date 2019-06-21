import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree
import re

class CinemarkSpider(scrapy.Spider):
    name = "cinemark"
    domain = 'https://www.cinemark.com/marketing-areas'
    request_url = 'https://www.cinemark.com'
    uid_list = []
    cities = []

    def __init__(self):
        with open('citiesusca.json', 'rb') as f:
            self.cities = json.load(f)
        

    def start_requests(self):
        url = self.domain
        yield scrapy.Request(url=url, callback=self.parse_state)
    
    def parse_state(self, response):
        link_list = response.xpath('//div[@class="columnList"]//h5//a')

        for cine_link in link_list:
            temp_url = cine_link.xpath('./@href').extract_first()
            cine_url = self.request_url + temp_url
            yield scrapy.Request(url=cine_url, callback=self.parse_stores)

    def parse_stores(self, response):
        link_list = response.xpath('//div[@class="theatreBlockInfo clearfix"]//h3//a')

        for detail_link in link_list:
            temp_url = detail_link.xpath('./@href').extract_first()
            cine_url = self.request_url + temp_url + '#theatreInfo'
            yield scrapy.Request(url=cine_url, callback=self.parse_detail)
    
    def parse_detail(self,response):
        if response:
            item = ChainItem()
            temp_name = response.xpath('//h1[@class="theatreName"]/text()').extract_first()
            print(temp_name)
            item['store_name'] = temp_name
            temp_address = response.xpath('//div[@class="theatreContactInfo clearfix"]/div[@class="left clearfix"]/div[@class="addressBody"]/text()').extract_first().strip()
            addr_list = re.sub("[^\w]", " ",  temp_address).split()
            print(addr_list)
            addr_string = re.sub("[^\w]", " ",  temp_address)
            
            total_count = 0
            for addr in addr_list:
                total_count += 1
            item['zip_code'] = addr_list[total_count - 1]
            item['state'] = addr_list[total_count - 2]
            print(item['zip_code'])
            print(item['state'])
            temp_address = ''
            temp_last = ''
            temp_city = ''
            temp_flag = 0
            first_flag = 0
            for a in addr_string:
                if temp_flag < 3:
                    if a != ' ':
                        if temp_flag != 0:
                            temp_address += ' ' + a
                            temp_flag = 0
                        else:
                            temp_address += a
                            temp_flag = 0
                    else:
                        temp_flag += 1
                else:
                    if a == ' ' and first_flag == 0:
                        item['address'] = temp_address
                        temp_address = ''
                        first_flag += 1
                    elif a == ' ' and first_flag != 0:
                        temp_last = temp_address
                    if a != ' ':
                        temp_flag = 0
                        temp_address = ''
                        temp_address += a

            temp_last = item['address']
            print(temp_last)
            temp_last_list = temp_last.split(' ')
            last_word = ''
            print(temp_last_list)
            for jk in temp_last_list:
                last_word = jk
            print(last_word)
            ok_flag = 0
            i = 0
            city_last = ''
            for addr in addr_list:
                if last_word == addr:
                    ok_flag = 1
                else:
                    if item['state'] != addr and item['zip_code'] != addr:
                        if ok_flag == 1:
                            city_last += addr + ' ' 
                    i += 1
            
            print(city_last)
            item['city'] = city_last
            item['country'] = 'United States'
            phone_temp = temp_address = response.xpath('//div[@class="theatreContactInfo clearfix"]/div[@class="right"]/text()').extract()
            phone = phone_temp[1].strip()
            print(phone)
            item['phone_number'] = phone
            
            yield item
