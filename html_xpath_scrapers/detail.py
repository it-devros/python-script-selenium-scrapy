# -*- coding: utf-8 -*-
import scrapy
import json
from Autism.items import AutismItem
import time
import datetime
import pdb



class DetailSpider(scrapy.Spider):

  name = 'detail'
  root_url = 'https://www.autismconnect.com'
  allowed_domain = 'https://www.autismconnect.com/directory/'
  start_url = 'https://www.autismconnect.com/directory/'

  detailUrls = []


  def __init__(self):
    with open('url.json', 'r') as f:
      details = json.loads(f.read())
      self.detailUrls = details
      f.close()


  def start_requests(self):
    url = self.start_url
    yield scrapy.Request(url=url, callback=self.parseDetail)


  def parseDetail(self, response):
    for detail in self.detailUrls:
      url = self.validateStr(detail['url'])
      yield scrapy.Request(url=url, callback=self.parseInfo)


  def parseInfo(self, response):
    details = response.xpath('//div[@class="directory-main"]//li')
    item  = AutismItem()
    item['ID'] = ''
    item['name'] = ''
    item['category'] = ''
    item['address'] = ''
    item['country'] = ''
    item['phone'] = ''
    item['email'] = ''
    item['website'] = ''
    item['image1'] = ''
    item['pageUrl'] = ''

    item['ID'] = self.getIDFromUrl(response.url)
    name = ''
    nameList = self.eliminateTextList(response.xpath('//div[@class="directory-heading"]//text()').extract())
    for na in nameList:
      name += na + ' '
    name = self.validateStr(name)
    item['name'] = name
    item['country'] = 'USA'
    item['pageUrl'] = response.url
    item['image1'] = self.validateStr(response.xpath('//div[@class="logo-img"]/img/@src').extract_first())

    for detail in details:
      icon = self.validateStr(detail.xpath('./span/i/@class').extract_first())
      value = ''
      valList = self.eliminateTextList(detail.xpath('./div//text()').extract())
      for val in valList:
        value += val + ' '
      value = self.validateStr(value)
      if icon == 'fa fa-hospital-o':
        item['category'] = value
      if icon == 'fa fa-map-marker':
        item['address'] = value
      if icon == 'fa fa-phone':
        item['phone'] = value
      if icon == 'fa fa-envelope':
        item['email'] = value
      if icon == 'fa fa-link':
        item['website'] = value

    item['phone'] = self.validateStr(item['phone'].replace(item['email'], '').replace(item['website'], ''))

    yield item



  def getIDFromUrl(self, url):
    try:
      tempList = url.split('/')
      length = len(tempList)
      tempList = tempList[length-1].split('?')
      return self.validateStr(tempList[0])
    except:
      return ''

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


