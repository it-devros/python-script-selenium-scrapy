import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree

class GwsupermarketSpider(scrapy.Spider):
  name = 'gwsupermarket'
  domain = 'http://www.gw-supermarket.com'
  start_url = 'http://www.gw-supermarket.com/en/store-information/'

  def start_requests(self):
    url = self.start_url
    yield scrapy.Request(url=url, callback=self.parse_stores)


  def parse_stores(self, response):
    store_lists = response.xpath('//div[@class="column_attr clearfix align_center"]')
    if store_lists:
      for store_li in store_lists:
        info_lists = store_li.xpath('.//p/text()').extract()
        i = 0
        address = ''
        temp_addr = ''
        phone = ''
        
        for info_li in info_lists:
          if info_li.find('Tel') != -1:
            phone = info_li
          i += 1
        count = i
        if info_lists[count - 1].find('open time') != -1:
          store_hours = info_lists[count - 1]
        else:
          store_hours = 'open time' + ': ' + info_lists[count - 1][5:]
        print(store_hours.encode('raw-unicode-escape'))
        store_name = info_lists[0]
        city = ''
        state = ''
        zip_code = ''
        if count == 5:
          if info_lists[3].find('Fax') != -1 or info_lists[4].find('Fax') != -1:
            temp_addr = info_lists[1]
            temp_list = temp_addr.split('. ')
            address = temp_list[0]
            temp_addr = temp_list[1]
            temp_list = temp_addr.split(' ')
            city = temp_list[0]
            state = temp_list[1]
            zip_code = temp_list[2]
            
          else:
            address = info_lists[1]
            temp_addr = info_lists[2]
            if temp_addr.find(',') != -1:
              temp_list = temp_addr.split(', ')
              city = temp_list[0]
              temp_addr = temp_list[1]
              if temp_addr.find(' ') != -1:
                temp_list = temp_addr.split(' ')
                state = temp_list[0]
                zip_code = temp_list[1]
                
              else:
                state = temp_addr[:2]
                zip_code = temp_addr[2:]
                
            else:
              city = temp_list[0]
              state = temp_list[1]
              zip_code = temp_list[2]
              
        else:
          address = info_lists[1]
          temp_addr = info_lists[2]
          if temp_addr.find(', ') != -1:
            temp_list = temp_addr.split(', ')
            k = 0
            for temp_li in temp_list:
              k += 1
            if k == 3:
              city = temp_list[0]
              print(city)
              temp_addr = temp_list[1]
              print(temp_addr)
              temp_list = temp_addr.split(' ')
              state = temp_list[0]
              zip_code = temp_list[1]
            
            else:
              if temp_list[1].find(' ') != -1:
                city = temp_list[0]
                print(city)
                temp_addr = temp_list[1]
                print(temp_addr)
                temp_list = temp_addr.split(' ')
                state = temp_list[0]
                zip_code = temp_list[1]
              else:
                print(temp_list)
                city = temp_list[0][:-2]
                state = temp_list[0][-2:]
                zip_code = temp_list[1]
              
          else:
            temp_list = temp_addr.split(' ')
            k = 0
            for temp_li in temp_list:
              k += 1
            if k == 3:
              print(temp_list)
              city = temp_list[0]
              state = temp_list[1]
              zip_code = temp_list[2]
              
            else:
              if temp_addr.encode('raw-unicode-escape').find('\uff0c') != -1:
                
                temp_str = temp_list[0].encode("utf-8").replace('\xe2', '')
                city = temp_str[:-5]
                print(city)
                state = temp_str[-2:]
                zip_code = temp_list[1]
                
              else:
                print(temp_list)
                city = temp_list[0] + ' ' + temp_list[1]
                state = temp_list[2]
                zip_code = temp_list[3]
                
        
        item = ChainItem()
        item['store_name'] = store_name
        item['address'] = address
        item['city'] = city
        item['state'] = state
        item['zip_code'] = zip_code
        item['country'] = 'United States'
        item['phone_number'] = phone
        item['store_hours'] = store_hours
        item['coming_soon'] = '0'

        yield item
        


          
