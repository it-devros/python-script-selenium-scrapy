# -*- coding: utf-8 -*-
import scrapy
import json
from MiamiDade.items import MiamidadeItem
import time
import pdb



class RealForeSpider(scrapy.Spider):

  name = 'realfore'
  allowed_domain = 'https://www.miamidade.realforeclose.com'

  root_url = "https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=C&PageDir=0&doR=1&tx=1536008931023&bypassPage=0&test=1&_=1536008931023"


  def start_requests(self):
    yield scrapy.Request('https://www.miamidade.realforeclose.com/index.cfm?zaction=ajax&zmethod=com&process=clock&showjson=false&_=1536008929918'
        , callback=self.parse_next
      )

  def parse_next(self, response):
    pdb.set_trace()
    today = self.now_milliseconds()
    url = "https://www.miamidade.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=UPDATE&FNC=LOAD&AREA=C&PageDir=0&doR=1&tx=" + str(today) + "&bypassPage=0&test=1&_=" + str(today)
    header = {
      "Accept": "application/json, text/javascript, */*; q=0.01",
      "Accept-Encoding": "gzip, deflate, br",
      "Cookie": "cfid=8f9a2729-29ac-406c-9d74-cfdc7c4feed5; cftoken=0; _ga=GA1.2.1507899272.1535991885; _gid=GA1.2.452450403.1535991885; __utmz=156495143.1535991885.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); CF_CLIENT_MIAMIDADE_REALFORECLOSE_TC=1536008776881; AWSELB=6FDF2BFD1CE9A81B0A727B5541DE86F11B7F6222DF458F597B4EE3AC90080CD2CEB5631813931A8190FB1DAA5C8219613D56CF0704FB06344C52F53120D15187D5A75139E2; __utma=156495143.1507899272.1535991885.1536001170.1536008778.4; __utmc=156495143; testcookiesenabled=enabled; __utmb=156495143.3.10.1536008778; CF_CLIENT_MIAMIDADE_REALFORECLOSE_LV=1536009919122; CF_CLIENT_MIAMIDADE_REALFORECLOSE_HC=109",
      "X-Requested-With": "XMLHttpRequest",
      "Upgrade-Insecure-Requests": "1",
      "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
    }
    yield scrapy.Request(url=self.root_url, callback=self.parseList, headers=header)


  def parseList(self, response):
    body =  json.loads(response.body)
    print body


  def now_milliseconds(self):
    return int(time.time() * 1000)


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