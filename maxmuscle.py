import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
import pdb
from bs4 import BeautifulSoup
import re
import datetime

class MaxmuscleSpider(scrapy.Spider):
    name = "maxmuscle"
    uid_list = []

    # def __init__(self):
    #     long_lat_fp = open('uscanplaces.csv', 'rb')
    #     self.long_lat_reader = csv.reader(long_lat_fp)
    
    def start_requests(self):
        seed = int((datetime.datetime.now()-datetime.datetime(1970,1,1)).total_seconds()) + 17967
        url = 'https://www.maxmuscle.com/locate-store?limit=5000&location=67205&timeCapt=' + str(seed)
        request = Request(url=url, callback=self.parse)
        yield request

    def parse(self, response):
        # pdb.set_trace()
        locs = json.loads(response.body.split('var flags = ')[1].split(';')[0].replace('\n', '').replace('\t', '').replace("'", '"'))
        locs = {ii[0]: (ii[1], ii[2]) for ii in locs}

        for store in response.xpath('//li[@style="margin-right:10px;"]'):
            info = store.xpath('./p[2]/text()').extract()
            info = [ii.strip() for ii in info if ii.strip()]
            
            item = {}
            item['store_name'] = store.xpath('.//h1/text()').extract_first()
            item['store_number'] = ''
            item['address'] = ' '.join(info[:-1])
            addr = info[-1]

            item['city'] = addr.split(', ')[0]
            item['state'] = addr.split(', ')[1].split(' ')[0]
            item['zip_code'] = addr.split(', ')[1].split(' ')[1]
            item['country'] = 'United States'
            item['phone_number'] = store.xpath('./p[2]/strong/text()').extract_first()
            item['latitude'] =  store.xpath('.//a[@class="point_on_map"]/@lat').extract_first()
            item['longitude'] =  store.xpath('.//a[@class="point_on_map"]/@lon').extract_first()
            #item['store_type'] = info_json["@type"]
            item['other_fields'] = ""
            item['coming_soon'] = "0"
            # self.uid_list.append(uid)
            # pdb.set_trace()
            item['store_hours'] = '; '.join([ii.strip() for ii in store.xpath('./p[3]/text()').extract()])
            yield item
