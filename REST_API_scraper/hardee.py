import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem

class JiffylubeSpider(scrapy.Spider):
    name = "jiffylube"
    request_url = "https://www.jiffylube.com/api/locations?lat=%s&lng=%s"
    uid_list = []

    def __init__(self):
        long_lat_fp = open('uscanplaces.csv', 'rb')
        self.long_lat_reader = csv.reader(long_lat_fp)
    
    def start_requests(self):
        for row in self.long_lat_reader:
            url = self.request_url % (row[0], row[1])
            yield scrapy.Request(url=url, callback=self.parse_store)

    # get longitude and latitude for a state by using google map.
    def parse_store(self, response):
        stores = json.loads(response.body)
        

    def validate(self, store, property):
        try:
            return store[property]
        except:
            return ""



