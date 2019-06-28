# -*- coding: utf-8 -*-
import scrapy
import json
from Opencnam.items import OpencnamItem
import math
import csv
import pdb


class OpencnamSpider(scrapy.Spider):

  name = 'opencnam'

  allowed_domain = 'https://api.opencnam.com'
  api_url = 'https://api.opencnam.com/v3/phone/'

  inputData = []


  def __init__(self):
    with open('inputs/input.csv', 'r') as f:
      reader = csv.reader(f)
      index = 0
      for row in reader:
        if index != 0:
          try:
            self.inputData.append({
              'phone': self.validateStr(row[2]),
              'country_code': self.validateStr(row[4])
            })
          except:
            print '=========== input data is not valid ============'
        index += 1
      
      f.close()

  def start_requests(self):
    for item in self.inputData:
      url = self.api_url + "+" + item['country_code'] + item['phone'] + "?account_sid=xxxxxxxxxxxxxxxxxxxx&auth_token=yyyyyyyyyyyyyyyyy"
      params = {
        'inputed_phone_number': item['phone'],
        'inputed_country_code': item['country_code']
      }
      yield scrapy.Request(url=url, callback=self.parseItem, meta=params)


  def parseItem(self, response):
    try:
      body = json.loads(response.body)
      item = PhoneItem()

      item['inputed_phone_number'] = response.meta['inputed_phone_number']
      item['inputed_country_code'] = response.meta['inputed_country_code']
      item['name'] = ''
      item['number'] = ''
      item['price'] = ''
      item['uri'] = ''

      item['name'] = body['name']
      item['number'] = body['number']
      item['price'] = body['price']
      item['uri'] = body['uri']

      yield item
    
    except:
      print '=========== body is not valid ============'
      with open('errors.txt', 'a+') as f:
        f.write(response.meta['inputed_phone_number'] + '\n')
        f.close()
    pass

  
  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return ''