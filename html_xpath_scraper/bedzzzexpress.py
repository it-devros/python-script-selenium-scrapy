import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class BedzzzexpressSpider(scrapy.Spider):
    name = 'bedzzzexpress'
    domain = 'https://bedzzzexpress.com'
    start_url = 'https://bedzzzexpress.com/best-mattress-locations/'

    def start_requests(self):
        url = self.start_url
        yield scrapy.Request(url=url, callback=self.parse_stores)


    def parse_stores(self, response):
        stores_link = response.xpath('//div[@class="block-grid-item"]//div[@class="panel panel-default"]//div//div[@class="panel-body"]//p//a/@href').extract()
        if stores_link:
            for store_link in stores_link:
                url = self.domain + store_link
                yield scrapy.Request(url=url, callback=self.parse_detail)
        else:
            print('++++++++++++++++++++++++ no store links')

    def parse_detail(self, response):
        store_info = response.xpath('//section[@class="zkeSubpage"]//div[@class="container"]//div[@class="row"]//div[@class="col-xs-12"]')
        if store_info:
            store_name = store_info.xpath('./h1/text()').extract_first().strip()
            store_hour_list = store_info.xpath('./div[@class="row"]//div')
            store_hour_div = store_hour_list[1]
            hour_list = store_hour_div.xpath('.//p/text()').extract()
            hours_header = store_hour_div.xpath('.//p//b/text()').extract()
            hours = ''
            i = 0
            for hour in hour_list:
                if hour.strip():
                    hours += hours_header[i].strip() + ' ' + hour.strip() + '; '
                    i += 1

            phone_div = store_hour_list[2]
            phone = phone_div.xpath('./a/text()').extract_first().strip()

            store_address = store_info.xpath('./div[@class="row"]//div[@class="col-sm-4 col-md-3"]//p/text()').extract()
            address = ''
            city = ''
            state = ''
            zip_code = ''
            i = 0
            for addr in store_address:
                if addr.strip():
                    if i == 0:
                        address = addr.strip()
                    if i == 1:
                        temp_str = addr.strip()
                        temp_list = temp_str.split(', ')
                        city = temp_list[0].strip()
                        temp_str = temp_list[1]
                        temp_list = temp_str.split(' ')
                        state = temp_list[0].strip()
                        zip_code = temp_list[1].strip()
                    i += 1

            item = ChainItem()
            item['store_name'] = store_name
            item['store_hours'] = hours
            if not item['store_hours']:
                item['coming_soon'] = '1'
            else:
                item['coming_soon'] = '0'
            item['phone_number'] = phone
            item['address'] = address
            item['city'] = city
            item['state'] = state
            item['zip_code'] = zip_code
            item['country'] = 'United States'
            yield item
        else:
            print('++++++++++++++++++++++++++ not store detail')
