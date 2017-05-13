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
import HTMLParser
import xml.etree.ElementTree as ET

class RubiosSpider(scrapy.Spider):
    name = 'rubios'
    request_url = 'https://www.rubios.com/store-location-data'
    uid_list = []
    

    def start_requests(self):
        
        yield scrapy.Request(url=self.request_url, callback=self.parse_store)
    
    def parse_store(self, response):
        stores_lists = json.loads(response.body)
        if stores_lists:
            stores = stores_lists['features']
            for stores_li in stores:
                temp_store_number = stores_li['properties']['Nid']
                if not temp_store_number in self.uid_list:
                    self.uid_list.append(temp_store_number)
                    item = ChainItem()
                    item['store_number'] = temp_store_number
                    item['store_name'] = stores_li['properties']['name']

                    # here i for store address.

                    temp_addr_string = stores_li['properties']['Street Address']

                    temp_addr_html = etree.HTML(temp_addr_string)
                    item['address'] = temp_addr_html.xpath('//div[@class="thoroughfare"]/text()')[0]
                    item['city'] = temp_addr_html.xpath('//span[@class="locality"]/text()')[0]
                    item['state'] = temp_addr_html.xpath('//span[@class="state"]/text()')[0]
                    item['zip_code'] = temp_addr_html.xpath('//span[@class="postal-code"]/text()')[0]
                    item['country'] = temp_addr_html.xpath('//span[@class="country"]/text()')[0]

                    item['phone_number'] = stores_li['properties']['Store Phone']
                    item['latitude'] = stores_li['geometry']['coordinates'][1]
                    item['longitude'] = stores_li['geometry']['coordinates'][0]
                    
                    # here is for store hours.
                    temp_string = stores_li['properties']['description']
                    temp_hour_string = temp_string.encode('unicode-escape')
                    temp_hour_html = etree.HTML(temp_hour_string)
                    final_hours = ''
                    temp_contents = temp_hour_html.xpath('//span[@class="oh-display"]')
                    if temp_contents:
                        for temp_content in temp_contents:
                            temp_texts = temp_content.xpath('.//span/text()')
                            print(temp_texts)
                            for temp_text in temp_texts:
                                final_hours += temp_text.strip()
                            final_hours += '; '
                        item['store_hours'] = final_hours
                    else:
                        item['store_hours'] = 'there are not store hours.'
                    
                    yield item
                else:
                    print('+++++++++++++++++++++++++++++ already scraped')

        else:
            print('++++++++++++++++ there are not stores')

        