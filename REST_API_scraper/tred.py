# -*- coding: utf-8 -*-
import scrapy
import json
from TredCars.items import TredcarsItem
import math
import pdb



class TredSpider(scrapy.Spider):
  name = 'tred'
  allowed_domain = 'https://www.tred.com'
  start_url = 'https://www.tred.com/api/listings'
  list_url = 'https://www.tred.com/api/listings/'

  condition_size = '?requestingPage=buy&status=active&page_size=25&'
  condition_pos = 'make=&model=&body_style=&zip=&distance=&'
  condition_date = 'year_start=2008&year_end=2014&'
  condition_price = 'price_min=1000&price_max=100000&'
  condition_miles = 'miles_min=5000&miles_max=100000&'
  condition_sort = 'sort=desc&sort_field=price&page='

  prefix = 0

  def __init__(self):
    monthlyInterest = 5.0 / 1200
    self.prefix = monthlyInterest / (1 - (math.pow(1 / (1 + monthlyInterest), 60)))


  def start_requests(self):
    url = self.start_url + self.condition_size + self.condition_pos + self.condition_date + self.condition_price + self.condition_miles + self.condition_sort
    yield scrapy.Request(url=url, callback=self.parse_Start)


  def parse_Start(self, response):
    body = json.loads(response.body)
    if body['total']:
      totalCount = body['total']
      pageSize = body['page_size']
      loopCount = int(body['total'] / body['page_size']) + 1
      for index in range(loopCount):
        if index != 0:
          url = self.start_url + self.condition_size + self.condition_pos + self.condition_date + self.condition_price + self.condition_miles + self.condition_sort + str(index)
          yield scrapy.Request(url=url, callback=self.parse_items)

  def parse_items(self, response):
    body = json.loads(response.body)
    if body['result'] and body['result']['cars']:
      for car in body['result']['cars']:
        param = {
          'year': car['year'],
          'make': car['make'],
          'model': car['model'],
          'submodel': car['trim'],
          'mileage': car['mileage'],
        }
        url = self.list_url + car['id'] + '/warranties'
        yield scrapy.Request(url=url, callback=self.parse_item, meta=param)


  def parse_item(self, response):
    prices = json.loads(response.body)

    if len(prices) > 0:
      item = TredcarsItem()
      item['year'] = response.meta['year']
      item['make'] = response.meta['make']
      item['model'] = response.meta['model']
      item['submodel'] = response.meta['submodel']
      item['mileage'] = response.meta['mileage']

      index = 0
      for price in prices:

        motnhly_float = price['retail'] * self.prefix
        monthly_int = int(motnhly_float)
        monthly = monthly_int
        diff = motnhly_float - monthly_int
        if diff > 0.5:
          monthly = math.ceil(motnhly_float)
        else:
          monthly = math.floor(motnhly_float)

        if index == 0:
          item['oneYearMonthly'] = int(monthly)
          item['oneYearTotal'] = price['retail']
        if index == 1:
          item['threeYearMonthly'] = int(monthly)
          item['threeYearTotal'] = price['retail']
        if index == 2:
          item['fiveYearMonthly'] = int(monthly)
          item['fiveYearTotal'] = price['retail']

        index = index + 1

      yield item

