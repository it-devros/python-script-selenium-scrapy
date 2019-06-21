# -*- coding: utf-8 -*-
import scrapy
import json
from wetherspoon.items import FoodItem
import math
import pdb


class FoodSpider(scrapy.Spider):

  name = 'food'
  allowed_domain = 'https://static.wsstack.nn4maws.net'
  root_url = 'https://static.wsstack.nn4maws.net/content/v1/menus'
  start_url = 'https://static.wsstack.nn4maws.net/content/v1/menus/474.json'

  venues = []

  def __init__(self):
    with open('venues.json', 'r') as f:
      venues = json.loads(f.read())
      self.venues = venues
      f.close()

  def start_requests(self):
    for venue in self.venues:
      url = self.root_url + '/' + str(venue['venueID']) + '.json'
      param = {
        'address': venue['address']
      }
      yield scrapy.Request(url=url, callback=self.parse_Foods, meta=param)

  def parse_Foods(self, response):
    body = json.loads(response.body)
    location_address = response.meta['address']

    venueName = ''
    try:
      venueName = body['venueName']
    except:
      print "---------- venue name not exist -------------"
      venueName = ''

    menus = []
    try:
      menus = body['menus']
    except:
      print "---------- menus not exist -------------"
      menus = []
    
    for menu in menus:

      menu_type = ''
      try:
        menu_type = menu['name']
      except:
        print "---------- menu_type not exist -------------"
        menu_type = ''
      
      subMenus = []
      try:
        subMenus = menu['subMenu']
      except:
        print "---------- subMenus not exist -------------"
        subMenus = []
      
      for subMenu in subMenus:

        sub_category = ''
        try:
          sub_category = subMenu['headerText']
        except:
          print "---------- sub_category not exist -------------"
          sub_category = ''
        
        addOns = []
        try:
          addOns = subMenu['addOns']
        except:
          print "---------- addOns not exist -------------"
          addOns = []

        products = []
        try:
          products = addOns['productChoices']
        except:
          print "---------- products not exist -------------"
          products = []
        
        for product in products:
          displayName = product['displayName']
          description = product['description']
          displayPrice = product['displayPrice']

          portions = []
          try:
            portions = product['portions']
          except:
            print "---------- portions not exist -------------"
            portions = []
          
          if len(portions) == 0:
            item = FoodItem()
            item['location_name'] = venueName
            item['location_address'] = location_address
            item['menu_type'] = menu_type
            item['sub_category'] = sub_category
            item['item_name'] = displayName
            item['item_description'] = description
            item['item_price'] = displayPrice
            item['item_size'] = ''
            yield item
          else:
            for portion in portions:
              item = FoodItem()
              item['location_name'] = venueName
              item['location_address'] = location_address
              item['menu_type'] = menu_type
              item['sub_category'] = sub_category
              item['item_name'] = displayName
              item['item_description'] = description
              item['item_price'] = portion['displayPrice']
              item['item_size'] = portion['name']
              yield item

        

        productGroups = []
        try:
          productGroups = subMenu['productGroups']
        except:
          print "---------- productGroups not exist -------------"
          productGroups = []
        
        for productGroup in productGroups:

          products = []
          try:
            products = productGroup['products']
          except:
            print "---------- products not exist -------------"
            products = []

          for product in products:
            displayName = product['displayName']
            description = product['description']
            displayPrice = product['displayPrice']

            portions = []
            try:
              portions = product['portions']
            except:
              print "---------- portions not exist -------------"
              portions = []
            
            if len(portions) == 0:
              item = FoodItem()
              item['location_name'] = venueName
              item['location_address'] = location_address
              item['menu_type'] = menu_type
              item['sub_category'] = sub_category
              item['item_name'] = displayName
              item['item_description'] = description
              item['item_price'] = displayPrice
              item['item_size'] = ''
              yield item
            else:
              for portion in portions:
                item = FoodItem()
                item['location_name'] = venueName
                item['location_address'] = location_address
                item['menu_type'] = menu_type
                item['sub_category'] = sub_category
                item['item_name'] = displayName
                item['item_description'] = description
                item['item_price'] = portion['displayPrice']
                item['item_size'] = portion['name']
                yield item
          


  


  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return ""