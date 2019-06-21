import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class SandellasSpider(scrapy.Spider):
    name = 'sandellas'
    domain = 'http://www.sandellas.com'
    start_url = 'http://www.sandellas.com/locations'

    def start_requests(self):
        url = self.start_url
        yield scrapy.Request(url=url, callback=self.parse_stores)
    
    def parse_stores(self, response):
        with open('log.html', 'a') as f:
            f.write(str(response))
            f.close()
        info_list = response.xpath('//div[@id="c3b7inlineContent"]//div//p')
        if info_list:
            i = 0
            for info in info_list:
                i += 0
            print(i)
        else:
            print('+++++++++++++++++++++++++++++++++ no response')