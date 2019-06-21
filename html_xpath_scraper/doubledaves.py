import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class DoubledavesSpider(scrapy.Spider):
    name = 'doubledaves'
    domain = 'http://www.doubledaves.com'
    start_url = 'http://www.doubledaves.com/locations/index.php'

    def start_requests(self):
        url = self.start_url
        frmdata = {'zipcode': '73301', 'searchradius': '5000', 'x': '10', 'y': '10'}
        yield FormRequest(url, callback=self.parse_stores, formdata=frmdata)
    
    def parse_stores(self, response):
        tr_list = response.xpath('//tr')
        if tr_list:
            for tr in tr_list:
                store_link = tr.xpath('.//td//p//a/@href').extract_first()
                store_text = tr.xpath('.//td//p//a/text()').extract_first()
                if store_link:
                    request_url = self.domain + store_link.encode('raw-unicode-escape').replace('\u2013', ' - ')
                    yield scrapy.Request(url=request_url, callback=self.parse_detail)
                if not store_link and store_text:
                    store_name = store_text.encode('raw-unicode-escape').replace('\u2013', ' - ')
                    store_name = store_name.replace(' - Coming Soon!', '')
                    str_lists = tr.xpath('.//td//p/text()').extract()
                    i = 0
                    addr = ''
                    city_state_zip = ''
                    for str_list in str_lists:
                        temp_str = str_list.encode('raw-unicode-escape').replace('\xa0', '').replace('\xc3', '').strip()
                        if temp_str != '':
                            if i == 0:
                                addr = temp_str
                                i += 1
                            elif i != 10:
                                city_state_zip = temp_str
                                i = 10
                    temp_list = city_state_zip.split(', ')
                    city = temp_list[0]
                    city_state_zip = temp_list[1]
                    temp_list = city_state_zip.split(' ')
                    state = temp_list[0]
                    zip_code = temp_list[1]

                    item = ChainItem()
                    item['store_name'] = "DoubleDave's Pizzaworks " + store_name
                    item['address'] = addr
                    item['city'] = city
                    item['state'] = state
                    item['zip_code'] = zip_code
                    item['country'] = 'United States'
                    item['coming_soon'] = '1'

                    yield item

        else:
            print('++++++++++++++++++++++++++++++++++ no stores')
    
    def parse_detail(self, response):
        store_name = response.xpath('//span[@class="fn org"]/text()').extract_first()
        if store_name:
            addr = response.xpath('//span[@class="street-address"]/text()').extract_first()
            city = response.xpath('//span[@class="locality"]/text()').extract_first()
            state = response.xpath('//abbr[@class="region"]/text()').extract_first()
            zip_code = response.xpath('//span[@class="postal-code"]/text()').extract_first()
            phone = response.xpath('//span[@class="tel"]/text()').extract_first()
            lat = response.xpath('//span[@property="latitude"]/@content').extract_first()
            lng = response.xpath('//span[@property="longitude"]/@content').extract_first()

            hours = response.xpath('//p[@id="untitled-region-5"]/text()').extract()
            if not hours:
                hours = response.xpath('//p[@id="untitled-region-3"]//strong/text()').extract()
            store_hours = ''
            for hour in hours:
                store_hours += hour.encode('raw-unicode-escape').replace('\xc3', '') + '; '
            item = ChainItem()
            item['store_name'] = store_name
            item['address'] = addr
            item['city'] = city
            item['state'] = state
            item['zip_code'] = zip_code
            item['phone_number'] = phone
            item['latitude'] = lat
            item['longitude'] = lng
            item['store_hours'] = store_hours
            item['country'] = 'United States'
            item['coming_soon'] = '0'

            yield item