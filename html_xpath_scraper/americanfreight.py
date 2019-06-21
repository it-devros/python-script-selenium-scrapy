import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class AmericanfreightSpider(scrapy.Spider):
    name = 'americanfreight'
    domain = 'https://www.americanfreight.us'
    start_url = 'https://www.americanfreight.us/storelocator/index/index?trackaddress=20010&trackdropdown=2000'

    def start_requests(self):
        url = self.start_url
        yield scrapy.Request(url=url, callback=self.parse_stores)
    
    def parse_stores(self, response):
        stores_link_eles = response.xpath('//ul[@id="list-store-detail"]//li[@class="el-content"]//div[@class="top-box-aff"]//div[@class="tag-store-aff"]//a')
        if stores_link_eles:
            for stores_link_ele in stores_link_eles:
                store_link = stores_link_ele.xpath('./@href').extract_first()
                store_name = stores_link_ele.xpath('./text()').extract_first().strip()
                temp_list = store_name.split('#')
                store_number = temp_list[1][:-1]
                request_url = self.domain + store_link
                request = scrapy.Request(url=request_url, callback=self.parse_detail)
                request.meta['store_number'] = store_number
                yield request
        

    def parse_detail(self, response):
        addr = response.xpath('//span[@itemprop="streetAddress"]/text()').extract_first()
        city = response.xpath('//meta[@itemprop="addressLocality"]/@content').extract_first()
        state = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
        zip_code = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()
        country = response.xpath('//span[@itemprop="countryName"]/text()').extract_first()
        phone = response.xpath('//span[@class="group-info"][@itemprop="telephone"]//a/text()').extract_first()
        
        hours = ''
        hour_list = response.xpath('//td/text()').extract()
        i = 0
        for hour in hour_list:
            if i % 2 == 0:
                hours += hour
            else:
                hours += hour + '; '
            i += 1

        num = response.meta['store_number']
        if addr:
            item = ChainItem()
            item['store_number'] = num
            item['address'] = addr
            item['city'] = city
            item['state'] = state
            item['zip_code'] = zip_code
            item['country'] = country
            item['phone_number'] = phone
            item['store_hours'] = hours

            yield item
