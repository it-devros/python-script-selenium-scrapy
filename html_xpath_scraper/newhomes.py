# -*- coding: utf-8 -*-
import scrapy
import json
from BuzzBuzzHome.items import BuzzbuzzhomeItem
import pdb


class NewhomesSpider(scrapy.Spider):
  name = 'newhomes'
  start_url = 'https://www.buzzbuzzhome.com'
  
  initial_url = 'https://www.buzzbuzzhome.com/us/united-states/california/san-francisco-new-homes'


  def start_requests(self):
    url = self.initial_url
    yield scrapy.Request(url=url, callback=self.parseBuildings)


  def parseBuildings(self, response):
    building_list = response.xpath("//ul[@class='dev-list']//a/@href").extract()
    for building in building_list:
      url = self.start_url + self.validateStr(building)
      yield scrapy.Request(url=url, callback=self.parseBuilding)


  def parseBuilding(self, response):
    name = self.validateStr(response.xpath("//div[@id='overview-card']/div[@id='basicInfoBox']/div[@class='main-info']/div[@class='name']/text()").extract_first())
    
    address_list = self.eliminateTextList(response.xpath("//div[@id='overview-card']//div[contains(@class, 'address-wrapper-wrapper')]/div[@class='address-wrapper']//text()").extract())
    address = ''
    for item in address_list:
      address = address + item + ' '
    address = self.validateStr(address)

    description_list = self.eliminateTextList(response.xpath("//div[@id='description']/div[@class='content-container']//text()").extract())
    description = ''
    for item in description_list:
      description = description + item + ' '
    description = self.validateStr(description)

    building_type = self.makeDetails(response, 1, 1, False)
    ownership = self.makeDetails(response, 1, 2, False)
    ceilings = self.makeDetails(response, 1, 3, False)
    selling_status = self.makeDetails(response, 1, 4, False)
    sales_started = self.makeDetails(response, 1, 5, False)
    construction_status = self.makeDetails(response, 1, 6, False)
    construction_started = self.makeDetails(response, 1, 7, False)

    estimated_completion = self.makeDetails(response, 2, 1, False)
    builders = self.makeDetails(response, 2, 3, True)
    architects = self.makeDetails(response, 2, 4, True)
    interior_designers = self.makeDetails(response, 2, 5, True)
    marketing_company = self.makeDetails(response, 2, 6, True)
    sales_company = self.makeDetails(response, 2, 7, True)

    amenities = []
    amenities_list = self.eliminateTextList(response.xpath("//div[@id='amenities']//span[@class='amenities-text']/text()").extract())
    for item in amenities_list:
      amenities.append(item)

    sales_price = self.makePrices(response, 1, 1)
    cost_purchasing_parking = self.makePrices(response, 1, 2)
    cost_purchasing_storage = self.makePrices(response, 1, 3)
    cc_maint = self.makePrices(response, 1, 4)

    deposit_structure = self.makePrices(response, 2, 1)
    co_op_fee_realtors = self.makePrices(response, 2, 2)
    percent_sold = self.makePrices(response, 2, 3)

    summary = ''
    summary_list = self.eliminateTextList(response.xpath("//div[@id='summary']/div[@class='content-text']/div[@class='summary-box-more']//text()").extract())
    for item in summary_list:
      summary = summary + item + ' '
    summary = self.validateStr(summary)

    sales_address = self.makeSalesCenter(response, 1, 1);
    available_time = self.makeSalesCenter(response, 1, 2);
    phone = self.makeSalesCenter(response, 2, 1)

    data = BuzzbuzzhomeItem()
    data['name'] = name
    data['address'] = address
    data['description'] = description

    data['building_type'] = building_type
    data['ownership'] = ownership
    data['ceilings'] = ceilings
    data['selling_status'] = selling_status
    data['sales_started'] = sales_started
    data['construction_status'] = construction_status
    data['construction_started'] = construction_started

    data['estimated_completion'] = estimated_completion
    data['builders'] = builders
    data['architects'] = architects
    data['interior_designers'] = interior_designers
    data['marketing_company'] = marketing_company
    data['sales_company'] = sales_company

    data['amenities'] = amenities

    data['sales_price'] = sales_price
    data['cost_purchasing_parking'] = cost_purchasing_parking
    data['cost_purchasing_storage'] = cost_purchasing_storage
    data['cc_maint'] = cc_maint

    data['deposit_structure'] = deposit_structure
    data['co_op_fee_realtors'] = co_op_fee_realtors
    data['percent_sold'] = percent_sold

    data['summary'] = summary
    data['sales_address'] = sales_address
    data['available_time'] = available_time
    data['phone'] = phone

    yield data



  def makeSalesCenter(self, response, first, second):
    value = ''
    temp_list = self.eliminateTextList(response.xpath("//div[@id='salesCenter']//div[contains(@class, 'content-container')][" + str(first) + "]/div[contains(@class, 'content-text')][" + str(second) + "]//text()").extract())
    for item in temp_list:
      value = value + item + ' '
    value = self.validateStr(value)
    return value


  def makePrices(self, response, first, second):
    value = ''
    temp_list = self.eliminateTextList(response.xpath("//div[@id='prices']//div[contains(@class, 'content-container')][" + str(first) + "]/div[contains(@class, 'content-text')][" + str(second) + "]//text()").extract())
    for item in temp_list:
      value = value + item + ' '
    value = self.validateStr(value)
    return value



  def makeDetails(self, response, first, second, a):
    if a == True:
      value = []
      temp_list = self.eliminateTextList(response.xpath("//div[@id='details']//div[contains(@class, 'content-container')][" + str(first) + "]/div[@class='content-text'][" + str(second) + "]//a/text()").extract())
      for item in temp_list:
        value.append(item)
      return value
    else:
      value = ''
      temp_list = self.eliminateTextList(response.xpath("//div[@id='details']//div[contains(@class, 'content-container')][" + str(first) + "]/div[@class='content-text'][" + str(second) + "]//text()").extract())
      for item in temp_list:
        value = value + item + ' '
      value = self.validateStr(value)
      return value


  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return ''


  def eliminateTextList(self, param):
    data = []
    for item in param:
      data.append(self.validateStr(item))
    return data



