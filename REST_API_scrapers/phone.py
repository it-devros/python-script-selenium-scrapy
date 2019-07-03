# -*- coding: utf-8 -*-
import scrapy
import json
from Phone.items import PhoneItem
import math
import csv
import pdb


class PhoneSpider(scrapy.Spider):

  name = 'phone'

  allowed_domain = 'https://proapi.whitepages.com'
  api_url = 'https://proapi.whitepages.com/3.0/phone_intel?api_key=xxxxxxxxxxxxxxxxx&phone='

  inputData = []


  def __init__(self):
    with open('inputs/no_return.csv', 'r') as f:
      reader = csv.reader(f)
      index = 0
      for row in reader:
        if index != 0:
          temp = row[0].split(';')
          try:
            self.inputData.append({
              'phone': self.validateStr(temp[0]),
              'country_code': self.validateStr(temp[1])
            })
          except:
            print '=========== input data is not valid ============'
        index += 1
      
      f.close()

  def start_requests(self):
    for item in self.inputData:
      url = self.api_url + item['phone'] + "&phone.country_hint=" + item['country_code']
      params = {
        'phone': item['phone']
      }
      yield scrapy.Request(url=url, callback=self.parseItem, meta=params)


  def parseItem(self, response):
    body = json.loads(response.body)
    
    try:
      item = PhoneItem()

      item['ID'] = ''
      item['inputed_phone_number'] = response.meta['phone']
      item['phone_number'] = ''
      item['is_valid'] = ''
      item['country_calling_code'] = ''
      item['country_code'] = ''
      item['country_name'] = ''
      item['line_type'] = ''
      item['carrier'] = ''
      item['is_prepaid'] = ''
      item['error'] = ''
      item['warnings'] = ''

      item['ID'] = body['id']
      item['phone_number'] = body['phone_number']
      item['is_valid'] = body['is_valid']
      item['country_calling_code'] = body['country_calling_code']
      item['country_code'] = body['country_code']
      item['country_name'] = body['country_name']
      item['line_type'] = body['line_type']
      item['carrier'] = body['carrier']
      item['is_prepaid'] = body['is_prepaid']
      item['error'] = body['error']
      item['warnings'] = body['warnings']

      yield item
    
    except:
      print '=========== body is not valid ============'
      print body
      with open('errors.txt', 'a+') as f:
        f.write(response.meta['phone'] + '\n')
        f.close()
    pass

  
  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return ''