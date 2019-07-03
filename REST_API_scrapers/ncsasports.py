# -*- coding: utf-8 -*-
import scrapy
import json
from Ncsasports.items import NcsasportsItem
import math
import pdb



class NcsasportsSpider(scrapy.Spider):

  name = 'ncsasports'

  start_url = 'https://coach.ncsasports.org'
  login_url = 'https://coach.ncsasports.org/coach/coach/j_spring_security_check'
  search_url = 'https://coach.ncsasports.org/coach/coachrms/searches/results'
  root_url = "https://recruit-match.ncsasports.org/clientrms/athletes/"
  index_url = 'https://coach.ncsasports.org/coach/coachrms/searches/results/main?graduationYears=2013&graduationYears=2025'


  def start_requests(self):
    url = self.login_url
    formdata = {
      "j_app_name": "coach",
      "spring-security-redirect": "/coachrms/login?login_error=1",
      "passwordLookup": "",
      "_spring_security_remember_me": "true",
      "j_username": "ebozeman@oru.edu",
      "j_password": "coachbozeman22",
      "_submit": "Log In"
    }
    yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.navigateFirst)



  def navigateFirst(self, response):
    url = self.index_url
    yield scrapy.Request(url=url, callback=self.startSearch)



  def startSearch(self, response):
    url = self.search_url
    page = 1
    formdata = {
      "page": str(page)
    }
    param = {
      "page": page
    }
    yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, meta=param, callback=self.parseList)



  def parseList(self, response):
    data = json.loads(response.body)
    query_id = data['query_id']
    try:
      items = data['results']
    except:
      items = []
    for item in items:
      url = self.root_url + str(item['client_id']) + '?accessType=COACH_QUERY&query_id=' + str(query_id)
      param = {
        "id": str(item['client_id']),
        "fullname": item['first_name'] + " " + item['last_name'],
        "star_rating": str(item['star_rating']),
        "graduation_year": str(item['graduation_year']),
        "primary_position": item['primary_position'],
        "other_positions": item['other_positions'],
        "height_feet": str(item['height_feet']),
        "height_inches": str(item['height_inches']),
        "weight": str(item['weight']),
        "gpa": str(item['gpa']),
        "high_school_name": item['high_school_name'],
        "client_city": item['client_city'],
        "client_state_code": item['client_state_code'],
        "zip": item['zip'],
        "thumbnail_url": item['thumbnail_url'],
        "handed": item['handed'],
        "measurables_display": item['measurables_display'],
      }
      yield scrapy.Request(url=url, meta=param, callback=self.parseDetail)

    if response.meta['page'] < 676:
      url = self.search_url
      page = response.meta['page'] + 1
      formdata = {
        "page": str(page)
      }
      param = {
        "page": page
      }
      yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, meta=param, callback=self.parseList)



  def parseDetail(self, response):
    client_id = response.meta['id']

    try:
      email = self.eliminateTextList(response.xpath('//div[@data-id="' + client_id + '"][1]//div[@class="container"]/div[@class="client-data"]/div[@class="client-info"]/div[@class="contact"]/a[1]/text()').extract())
    except:
      email = ""

    try:
      phone = self.eliminateTextList(response.xpath('//div[@data-id="' + client_id + '"][1]//div[@class="container"]/div[@class="client-data"]/div[@class="client-info"]/div[@class="contact"]/a[2]/text()').extract())
    except:
      phone = ""

    references = []
    referencesItems = response.xpath('//div[@data-id="' + client_id + '"][1]//section[@id="coach-references-section"]/ul/li')
    for item in referencesItems:
      ref_name = self.validateStr(item.xpath('./div[1]/text()').extract_first())
      ref_type = self.validateStr(item.xpath('./div[2]/text()').extract_first())
      ref_phone = self.validateStr(item.xpath('./div[3]/text()').extract_first())
      ref_email = self.validateStr(item.xpath('./div[4]/text()').extract_first())
      references.append({
        "name": ref_name,
        "type": ref_type,
        "phone": ref_phone,
        "email": ref_email
      })

    contacts = []
    contactsItems = response.xpath('//div[@data-id="' + client_id + '"][1]//section[@id="contact-section"]/div[1]/div')
    for item in contactsItems:
      contact_name = self.eliminateTextList(item.xpath('./h5/text()').extract())
      contact_items = self.eliminateTextList(item.xpath('.//a/text()').extract())
      contacts.append({
        "name": contact_name,
        "items": contact_items
      })

    item = NcsasportsItem()

    item['Id'] = ""
    item['fullname'] = ""
    item['star_rating'] = ""
    item['graduation_year'] = ""
    item['primary_position'] = ""
    item['other_positions'] = ""
    item['height_feet'] = ""
    item['height_inches'] = ""
    item['weight'] = ""
    item['gpa'] = ""
    item['high_school_name'] = ""
    item['client_city'] = ""
    item['client_state_code'] = ""
    item['zipcode'] = ""
    item['thumbnail_url'] = ""
    item['handed'] = ""
    item['measurables_display'] = ""
    item['email'] = ""
    item['phone'] = ""
    item['references'] = ""
    item['contacts'] = ""

    item['Id'] = response.meta['id']
    item['fullname'] = response.meta['fullname']
    item['star_rating'] = response.meta['star_rating']
    item['graduation_year'] = response.meta['graduation_year']
    item['primary_position'] = response.meta['primary_position']
    item['other_positions'] = response.meta['other_positions']
    item['height_feet'] = response.meta['height_feet']
    item['height_inches'] = response.meta['height_inches']
    item['weight'] = response.meta['weight']
    item['gpa'] = response.meta['gpa']
    item['high_school_name'] = response.meta['high_school_name']
    item['client_city'] = response.meta['client_city']
    item['client_state_code'] = response.meta['client_state_code']
    item['zipcode'] = response.meta['zip']
    item['thumbnail_url'] = response.meta['thumbnail_url']
    item['handed'] = response.meta['handed']
    item['measurables_display'] = response.meta['measurables_display']
    item['email'] = email
    item['phone'] = phone
    item['references'] = references
    item['contacts'] = contacts
    
    yield item




  def validateStr(self, string):
    try:
      return string.strip()
    except:
      return ""


  def eliminateTextList(self, param):
    data = ""
    for item in param:
      temp = self.validateStr(item)
      if temp:
        data = data + temp + ", "
    data = data[:-2]
    return data

