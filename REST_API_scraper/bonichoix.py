import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree


class BonichoixSpider(scrapy.Spider):
    name = 'bonichoix'
    domain = 'https://www.bonichoix.com/'
    request_url = 'https://www.bonichoix.com/trouver/get_magasins'
    canada_state_list = ['BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
    cities = []
    uid_list = []

    def __init__(self):
        with open('canada_city_list.json', 'rb') as f:
            self.cities = json.load(f)

    def start_requests(self):
        url = self.request_url
        for city in self.cities:
            if city[1] in self.canada_state_list:
                frmdata = {'ville': city[0]}
                yield FormRequest(url, callback=self.parse_stores, formdata=frmdata)
    
    def parse_stores(self, response):
        stores_list = json.loads(response.body)
        if stores_list['magasins']:
            for store in stores_list['magasins']:
                store_number = store['magasin_num']
                if not store_number in self.uid_list:
                    self.uid_list.append(store_number)
                    item = ChainItem()
                    item['store_name'] = store['magasin_nom']
                    item['store_number'] = store['magasin_num']
                    item['address'] = store['magasin_adr']
                    item['zip_code'] = store['magasin_cp']
                    item['state'] = store['province_lib']
                    item['city'] = store['ville_lib']
                    item['latitude'] = store['magasin_latitude']
                    item['longitude'] = store['magasin_longitude']
                    item['phone_number'] = store['magasin_indicatif_tel'] + '-' + store['magasin_tel']
                    item['coming_soon'] = '0'
                    yield item
