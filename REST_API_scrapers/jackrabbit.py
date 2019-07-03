import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html

class JackrabbitSpider(scrapy.Spider):
  name = 'jackrabbit'
  domain = 'https://www.jackrabbit.com'
  request_url = 'https://a.tiles.mapbox.com/v4/chchchawes.pjli078d/features.json?access_token=pk.eyJ1IjoiY2hjaGNoYXdlcyIsImEiOiJjaW1udGN3djEwMDFndmtreTFvYm0waWw0In0.t4gR2FndaeaE1i5bCEUFzA'

  def start_requests(self):
    url = self.request_url
    yield scrapy.Request(url=url, callback=self.body)
  
  def body(self, response):
    print('================================ checking.......')
    if response.body:
      stores_list = json.loads(response.body)
      for store in stores_list['features']:
        item = ChainItem()
        item['latitude'] = store['geometry']['coordinates'][1]
        item['longitude'] = store['geometry']['coordinates'][0]
        item['store_name'] = store['properties']['title']
        item['store_number'] = store['properties']['id']
        description = store['properties']['description']
        temp_list = description.replace('<BR>', '<br>').replace('<Br>', '<br>').replace('<bR>', '<br>').split('<br>')
        description = temp_list[0]
  
        address = ''
        city = ''
        zip_code = ''
        state = ''
        desc_list = description.split(', ')
        i = 0
        for desc in desc_list:
          i += 1
        if desc_list[i - 1].strip().find('NY') == -1:
          zip_code = desc_list[i - 1].strip()
        
        if i > 2:
          if desc_list[1].find('NY') != -1:
            zip_code = desc_list[2].strip()
            state = desc_list[1].strip()
            temp_list = desc_list[0].split('New York')
            address = temp_list[0]
            city = 'New York'
          else:
            address = desc_list[0]
            flag_addr = 0
            if desc_list[1].find('#') != -1:
              flag_addr = 1
            description = desc_list[1]
            desc_list = description.split(' ')
            j = 0
            for desc in desc_list:
              j += 1
            state = desc_list[j - 1]
            k = 0
            if flag_addr == 1:
              address += desc_list[0]
              k = 1
            else:
              k = 0
            while k < j - 1:
              city += desc_list[k] + ' '
              k += 1
        elif i == 2:
          description = desc_list[0]
          desc_list = description.split(' ')
          j = 0
          for desc in desc_list:
            j += 1
          state = desc_list[j - 1]
          temp_desc = ''
          k = 0
          while k < j - 1:
            temp_desc += desc_list[k] + ' '
            k += 1
          if temp_desc.find('Street') != -1:
            temp_list = temp_desc.split('Street')
            address = temp_list[0].strip() + ' ' + 'Street'
            city = temp_list[1].strip()
          elif temp_desc.find('St') != -1:
            temp_list = temp_desc.split('St')
            address = temp_list[0].strip() + ' ' + 'St'
            city = temp_list[1].strip()
          elif temp_desc.find('D.') != -1:
            temp_list = temp_desc.split('D.')
            address = temp_list[0].strip() + ' ' + 'D.'
            city = temp_list[1].strip()
          elif temp_desc.find('Avenue') != -1:
            temp_list = temp_desc.split('Avenue')
            address = temp_list[0].strip() + ' ' + 'Avenue'
            city = temp_list[1].strip()
          elif temp_desc.find('Ave') != -1:
            temp_list = temp_desc.split('Ave')
            address = temp_list[0].strip() + ' ' + 'Ave'
            city = temp_list[1].strip()
          elif temp_desc.find('Road') != -1:
            temp_list = temp_desc.split('Road')
            address = temp_list[0].strip() + ' ' + 'Road'
            city = temp_list[1].strip()
          elif temp_desc.find('Rd') != -1:
            temp_list = temp_desc.split('Rd')
            address = temp_list[0].strip() + ' ' + 'Rd'
            city = temp_list[1].strip()
          else:
            city = desc_list[j - 2]
            k = 0
            while k < j - 2:
              temp_desc += desc_list[k] + ' '
              k += 1
            address = temp_desc

        item['zip_code'] = zip_code
        item['city'] = city
        item['state'] = state
        item['address'] = address
        description = store['properties']['description'].replace('<bR>', '<br>').replace('<BR>', '<br>').replace('<Br>', '<br>')
        temp_list = description.split('<br>')
        temp_str = temp_list[1]
        temp_list = temp_str.split('<br><br>')
        phone = temp_list[0].strip()
        item['phone_number'] = phone
        temp_list = description.split('</strong>')
        temp_str = temp_list[1].replace('<br>', '').replace('\n', '; ').split('<a href')
        hours = temp_str[0]
        print hours
        item['store_hours'] = hours
        if item['store_hours']:
          item['coming_soon'] = '0'
        else:
          item['coming_soon'] = '1'
        item['country'] = 'United States'
        
        yield item
    else:
      print('===================================== no response')