# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest
import json
from ProductHunter.items import ProducthunterItem
import math
import pdb
import datetime
import json


class ProductHunterSpider(scrapy.Spider):
  name = 'productHunter'
  allowed_domain = 'https://www.producthunt.com'

  start_url = 'https://www.producthunt.com/time-travel'
  api_url = 'https://www.producthunt.com/frontend/graphql'

  def start_requests(self):
    endDate = datetime.datetime(2019, 6, 1)
    currentDate = datetime.datetime(2018, 6, 1)

    headers = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
      'content-type': 'application/json',
      'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
      'x-requested-with': 'XMLHttpRequest'
    }

    body = {
      "operationName": "Posts",
      "query": "query Posts($year: Int, $month: Int, $day: Int, $cursor: String) {\n  posts(first: 1000, year: $year, month: $month, day: $day, after: $cursor) {\n    edges {\n      node {\n        id\n        ...PostItemList\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment PostItemList on Post {\n  id\n  ...PostItem\n  __typename\n}\n\nfragment PostItem on Post {\n  id\n  _id\n  comments_count\n  name\n  shortened_url\n  slug\n  tagline\n  updated_at\n  ...CollectButton\n  ...PostThumbnail\n  ...PostVoteButton\n  ...TopicFollowButtonList\n  __typename\n}\n\nfragment CollectButton on Post {\n  id\n  name\n  isCollected\n  __typename\n}\n\nfragment PostThumbnail on Post {\n  id\n  name\n  thumbnail {\n    id\n    media_type\n    ...MediaThumbnail\n    __typename\n  }\n  ...PostStatusIcons\n  __typename\n}\n\nfragment MediaThumbnail on Media {\n  id\n  image_uuid\n  __typename\n}\n\nfragment PostStatusIcons on Post {\n  name\n  product_state\n  __typename\n}\n\nfragment PostVoteButton on Post {\n  _id\n  id\n  featured_at\n  updated_at\n  disabled_when_scheduled\n  has_voted\n  ... on Votable {\n    id\n    votes_count\n    __typename\n  }\n  __typename\n}\n\nfragment TopicFollowButtonList on Topicable {\n  id\n  topics {\n    edges {\n      node {\n        id\n        ...TopicFollowButton\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment TopicFollowButton on Topic {\n  id\n  slug\n  name\n  isFollowed\n  ...TopicImage\n  __typename\n}\n\nfragment TopicImage on Topic {\n  name\n  image_uuid\n  __typename\n}\n"
    }

    while currentDate < endDate:

      yearStr = currentDate.strftime('%Y')
      monthStr = currentDate.strftime('%m')
      dayStr = currentDate.strftime('%d')
      
      year = int(yearStr)
      month = int(monthStr)
      day = int(dayStr)

      body["variables"] = {
        "year": year,
        "month": month,
        "day": day,
        "cursor": "",
        "includeLayout": False
      }

      param = {
        'timestamp': yearStr + '-' + monthStr + '-' + dayStr
      }

      yield scrapy.Request(url=self.api_url, method="post", callback=self.parse_List, headers=headers, body=json.dumps(body), meta=param)

      currentDate = currentDate + datetime.timedelta(days=1)


  def parse_List(self, response):
    body = json.loads(response.body)
    if body['data'] and body['data']['posts'] and body['data']['posts']['edges']:
      if len(body['data']['posts']['edges']) > 0:
        for item in body['data']['posts']['edges']:
          url = 'https://www.producthunt.com/posts/' + item['node']['slug']
          param = {
            'timestamp': response.meta['timestamp'],
            'product_name': item['node']['name'],
            'description': item['node']['tagline'],
            'ph_topic': '',
            'internal_link': url
          }
          temp = ''
          if item['node']['topics'] and item['node']['topics']['edges']:
            if len(item['node']['topics']['edges']) > 0:
              for topic in item['node']['topics']['edges']:
                temp = temp + topic['node']['name'] + ', '
          param['ph_topic'] = temp
          yield scrapy.Request(url=url, callback=self.parse_item, meta=param)

  
  def parse_item(self, response):
    external_link = ''
    try:  
      tempList = response.body.split('"redirect_path":"')
      tempList = tempList[1].split('",')
      external_link = 'https://www.producthunt.com' + tempList[0]
    except:
      external_link = ''
    
    item = ProducthunterItem()
    item['timestamp'] = response.meta['timestamp']
    item['product_name'] = response.meta['product_name']
    item['description'] = response.meta['description']
    item['ph_topic'] = response.meta['ph_topic']
    item['internal_link'] = response.meta['internal_link']
    item['external_link'] = external_link

    yield item


