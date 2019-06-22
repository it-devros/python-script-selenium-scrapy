# -*- coding: utf-8 -*-
import scrapy
import json
from Architecture.items import ArchitectureItem
import math
import pdb



class ArchitectureSpider(scrapy.Spider):

  name = 'architecture'
  allowed_domain = 'https://members.architecture.com'

  start_url = 'https://members.architecture.com/directory/default.asp?dir=3'
  search_url = 'https://members.architecture.com/directory/search.asp?dir=3'


  def start_requests(self):
    url =  self.start_url
    yield scrapy.Request(url=url, callback=self.parseSearchKey)


  def parseSearchKey(self, response):
    csrfToken = self.validateStr(response.xpath('//input[@id="CSRFToken"]/@value').extract_first())
    formGuid = self.validateStr(response.xpath('//input[@name="FormGuid"]/@value').extract_first())
    countryList = self.eliminateTextList(response.xpath('//select[@id="country"]//option/@value').extract())

    for country in countryList:
      url = self.search_url
      formdata = {
        'CSRFToken': csrfToken,
        'FormGuid': formGuid,
        'NameType': '1',
        'Name': '',
        'AddType': '1',
        'Address': '',
        'PostCode': '',
        'country': country,
        'submit1': 'Submit'	
      }
      param = {
        'page': 1
      }
      yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.parseList, meta=param)


  def parseList(self, response):
    detailList = self.eliminateTextList(response.xpath('//div[@id="ribacontent"]/table//a[@class="text"]/@href').extract())
    for detail in detailList:
      url = self.allowed_domain + detail.replace('..', '')
      yield scrapy.Request(url=url, callback=self.parseDetail)

    pageNationList = self.eliminateTextList(response.xpath('//p[@class="Notes"]/b/text()').extract())
    try:
      if int(pageNationList[1]) != int(pageNationList[2]):
        csrfToken = self.validateStr(response.xpath('//input[@id="CSRFToken"]/@value').extract_first())
        formGuid = self.validateStr(response.xpath('//input[@name="FormGuid"]/@value').extract_first())
        qt = self.validateStr(response.xpath('//input[@id="qt"]/@value').extract_first())
        queryState = self.validateStr(response.xpath('//input[@id="QueryState"]/@value').extract_first())
        sqlHash = self.validateStr(response.xpath('//input[@id="sqlhash"]/@value').extract_first())
        pg = str(response.meta['page'] + 1)

        url = self.search_url
        formdata = {
          'CSRFToken': csrfToken,
          'FormGuid': formGuid,
          'pg': pg,
          'qt': qt,
          'QueryState': queryState,
          'sqlhash': sqlHash
        }
        param = {
          'page': response.meta['page'] + 1
        }
        yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.parseList, meta=param)
    except:
      pass


  def parseDetail(self, response):
    item = ArchitectureItem()

    item['name'] = ''
    item['address'] = ''
    item['phone'] = ''
    item['email'] = ''
    item['website'] = ''

    item['name'] = self.validateStr(response.xpath('//div[@id="ribacontent"]/table[@class="projects"]//td[@class="Title"]/h4/text()').extract_first())

    infoList = response.xpath('//div[@id="ribacontent"]/form[@id="form1"]/table[@class="projects"]//tr')
    for info in infoList:
      title = self.validateStr(info.xpath('.//td[1]/img/@title').extract_first())
      if title == 'Address':
        addrList = self.eliminateTextList(info.xpath('.//td[2]/text()').extract())
        address = ''
        for addr in addrList:
          address += addr + " "
        item['address'] = self.validateStr(address)
      if title == 'Telephone':
        item['phone'] = self.validateStr(info.xpath('.//td[2]/text()').extract_first())
      if title == 'Email':
        item['email'] = self.validateStr(info.xpath('.//td[2]/a/text()').extract_first())
      if title == 'Website':
        item['website'] = self.validateStr(info.xpath('.//td[2]/a/text()').extract_first())

    yield item




  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return False


  def eliminateTextList(self, param):
    data = []
    for item in param:
      temp = self.validateStr(item)
      if temp:
        data.append(temp)
    return data