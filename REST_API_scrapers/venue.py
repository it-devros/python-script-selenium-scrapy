# -*- coding: utf-8 -*-
import scrapy
import json
from wetherspoon.items import VenueItem
import math
import pdb


class VenuesSpider(scrapy.Spider):

  name = 'venues'
  allowed_domain = 'https://static.wsstack.nn4maws.net'
  start_url = 'https://static.wsstack.nn4maws.net/v1/venues/en_gb/venues.json'

  def start_requests(self):
    url = self.start_url
    yield scrapy.Request(url=url, callback=self.parse_Venues)

  def parse_Venues(self, response):
    body = json.loads(response.body)
    if body['venues']:
      venues = body['venues']
      index = 0
      for venue in venues:
        item = VenueItem()
        item['venueID'] = venue['venueId']
        item['address'] = ''
        temp = ''
        if venue['line1'] != '':
          temp = temp + venue['line1']
        if venue['line2'] != '':
          temp = temp + ', ' + venue['line2']
        if venue['postcode'] != '':
          temp = temp + ', ' + venue['postcode']
        if venue['town'] != '':
          temp = temp + ', ' + venue['town']
        if venue['county'] != '':
          temp = temp + ', ' + venue['county']
        if venue['country'] != '':
          temp = temp + ', ' + venue['country']
        item['address'] = self.validateStr(temp)

        yield item
  
  def validateStr(self, string):
    try:
      return string.replace(u'\u2013', '-').replace(u'\u2019', "'").strip()
    except:
      return ""
