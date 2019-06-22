# -*- coding: utf-8 -*-
import scrapy
import json
from Ncsasports.items import NcsasportsOriginItem
import math
import pdb



class NcsaSpider(scrapy.Spider):

  name = 'ncsa'

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
    try:
      data = json.loads(response.body.decode('utf-8', 'ignore'))
    except:
      data = {}
    if data:
      query_id = data['query_id']
      try:
        items = data['results']
      except:
        items = []
      for item in items:
        url = self.root_url + str(item['client_id']) + '?accessType=COACH_QUERY&query_id=' + str(query_id)
        result = NcsasportsOriginItem()
        result['Id'] = ""
        result['fullname'] = ""
        result['star_rating'] = ""
        result['graduation_year'] = ""
        result['primary_position'] = ""
        result['other_positions'] = ""
        result['height_feet'] = ""
        result['height_inches'] = ""
        result['weight'] = ""
        result['gpa'] = ""
        result['high_school_name'] = ""
        result['client_city'] = ""
        result['client_state_code'] = ""
        result['zipcode'] = ""
        result['thumbnail_url'] = ""
        result['handed'] = ""
        result['measurables_display'] = ""
        result['email'] = ""
        result['phone'] = ""
        result['references'] = ""
        result['contacts'] = ""
        result['url'] = ""

        result['Id'] = item['client_id']
        result['fullname'] = item['first_name'] + " " + item['last_name']
        result['star_rating'] = item['star_rating']
        result['graduation_year'] = item['graduation_year']
        result['primary_position'] = item['primary_position']
        result['other_positions'] = item['other_positions']
        result['height_feet'] = item['height_feet']
        result['height_inches'] = item['height_inches']
        result['weight'] = item['weight']
        result['gpa'] = item['gpa']
        result['high_school_name'] = item['high_school_name']
        result['client_city'] = item['client_city']
        result['client_state_code'] = item['client_state_code']
        result['zipcode'] = item['zip']
        result['thumbnail_url'] = item['thumbnail_url']
        result['handed'] = item['handed']
        result['measurables_display'] = item['measurables_display']
        result['url'] = url

        yield result
    else:
      print "============================ data error ====================="

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

