import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class WestelmSpider(scrapy.Spider):
    name = 'westelm'
    domain = 'http://www.westelm.com'
    request_us_url = 'http://www.westelm.com/search/stores.json?lat=37.60969&lng=-97.339772&radius=20000&brands=WE'
    

    def start_requests(self):
        url = self.request_us_url
        yield scrapy.Request(url=url, callback=self.parse_stores)

    def parse_stores(self, response):
        stores = json.loads(response.body)
        if stores:
            for store in stores['storeListResponse']['stores']:
                item = ChainItem()
                item['store_number'] = store['properties']['STORE_NUMBER']
                item['address'] = store['properties']['ADDRESS_LINE_1']
                item['longitude'] = store['properties']['LONGITUDE']
                item['address2'] = store['properties']['ADDRESS_LINE_2']
                item['phone_number'] = store['properties']['PHONE_NUMBER_FORMATTED']
                item['store_name'] = store['properties']['STORE_NAME']
                item['city'] = store['properties']['CITY']
                item['zip_code'] = store['properties']['POSTAL_CODE']
                item['state'] = store['properties']['STATE_PROVINCE']
                item['latitude'] = store['properties']['LATITUDE']
                if store['properties']['COUNTRY_CODE'] == 'US':
                    item['country'] = 'United States'
                else:
                    item['country'] = store['properties']['COUNTRY_CODE']
                item['coming_soon'] = '0'
                item['store_hours'] = 'Mon ' + store['properties']['MONDAY_HOURS_FORMATTED'] + '; ' + 'Tue ' + store['properties']['TUESDAY_HOURS_FORMATTED'] + '; ' + 'Wed ' + store['properties']['WEDNESDAY_HOURS_FORMATTED'] + '; ' + 'Thu ' + store['properties']['THURSDAY_HOURS_FORMATTED'] + '; ' + 'Fri ' + store['properties']['FRIDAY_HOURS_FORMATTED'] + '; ' + 'Sat ' + store['properties']['SATURDAY_HOURS_FORMATTED'] + '; ' + 'Sun ' + store['properties']['SUNDAY_HOURS_FORMATTED'] + '; '

                yield item
    
    