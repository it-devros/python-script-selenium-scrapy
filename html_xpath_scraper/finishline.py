import scrapy
import json
import csv
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from chainxy.items import ChainItem
from lxml import etree


class FinishlineSpider(scrapy.Spider):
  name = "finishline"
  
  state_list = ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','BC','AB','SK','MB','ON','QC','NB','NS','PE','NF','NT','YT']
  
  uid_list = []
  domain ='https://stores.finishline.com/'
   
  def start_requests(self):
    url = self.domain
    yield scrapy.Request(url=url, callback=self.parse_state)

  # get longitude and latitude for a state by using google map.
  def parse_state(self, response):
    states_link_list = response.xpath('//a[@class="c-directory-list-content-item-link"]')

    for state_link in states_link_list:
      temp_url = state_link.xpath('./@href').extract_first()
      state_url = self.domain + temp_url
      yield scrapy.Request(url=state_url, callback=self.parse_city)
    # state_url = self.domain + 'ca.html'
    # yield scrapy.Request(url=state_url, callback=self.parse_city)
    
  
  def parse_city(self, response):
    cities_link_list = response.xpath('//a[@class="c-directory-list-content-item-link"]')
    cities_stores_counts = response.xpath('//span[@class="c-directory-list-content-item-count"]')
    i = 0
    for city_link, city_store_count in zip(cities_link_list, cities_stores_counts):
      temp_url = city_link.xpath('./@href').extract_first()
      temp_count = city_store_count.xpath('./text()').extract_first()
      i += 1
      print("count numer ++++++++++++++++++", i)
      city_url = self.domain + temp_url
      if temp_count == '(1)':
        print("1111------------", temp_count)
        request = scrapy.Request(url=city_url, callback=self.parse_store)
        request.meta['city_url'] = city_url
        yield request
      else:
        yield scrapy.Request(url=city_url, callback=self.parse_stores)

  def parse_store(self, response):
    redirect_url = response.meta['city_url']
    phone_li = response.xpath('//span[@id="telephone"]')
    if not phone_li:
      item = ChainItem()
      temp_brand = response.xpath('.//div[@class="c-location-grid-top"]//h5[@class="c-location-grid-item-title"]//span[@class="location-name-brand"]/text()').extract_first()
      temp_geo = response.xpath('.//div[@class="c-location-grid-top"]//h5[@class="c-location-grid-item-title"]//span[@class="location-name-geo"]/text()').extract_first()
      item['store_name'] = temp_brand + temp_geo
      temp_addr = response.xpath('.//div[@class="c-location-grid-bottom"]//div[@class="c-location-grid-left"]//div[@class="c-location-grid-item-address"]//address[@class="c-address"]')
      item['address'] = temp_addr.xpath('.//span[@class="c-address-street"]//span[@class="c-address-street-1"]/text()').extract_first()
      temp_city = temp_addr.xpath('.//span[@class="c-address-city"]//span/text()').extract()
      item['city'] = temp_city[0]
      item['state'] = temp_addr.xpath('.//abbr[@class="c-address-state"]/text()').extract_first()
      item['zip_code'] = temp_addr.xpath('.//span[@class="c-address-postal-code"]/text()').extract_first()
      item['country'] = 'United States'
      item['coming_soon'] = '1'
      item['phone_number'] = response.xpath('.//div[@class="c-location-grid-bottom"]//div[@class="c-location-grid-right"]//div[@class="c-location-grid-item-phone"]//div//span/text()').extract_first()
      yield item
      
    else:
      item = ChainItem()
      temp_brand = response.xpath('//span[@class="location-name-brand"]/text()').extract_first()
      temp_geo = response.xpath('//span[@class="location-name-geo"]/text()').extract_first()
      item['store_name'] = temp_brand + temp_geo
      temp_addr1 = response.xpath('//span[@class="c-address-street-1"]/text()').extract_first()
      temp_addr2 = response.xpath('//span[@class="c-address-street-2"]/text()').extract_first()
      item['address'] = temp_addr1
      item['address2'] = temp_addr2
      temp_city = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
      item['city'] = temp_city
      temp_state = response.xpath('//abbr[@class="c-address-state"]/text()').extract_first()
      item['state'] = temp_state
      temp_zip = response.xpath('//span[@class="c-address-postal-code"]/text()').extract_first()
      item['zip_code'] = temp_zip
      temp_phone = response.xpath('//span[@id="telephone"]/text()').extract_first()
      item['phone_number'] = temp_phone
      temp_hours = ''
      temp_hours_list = response.xpath('//table[@class="c-location-hours-details"]//tbody//tr')
      if temp_hours_list:
        for temp_hour in temp_hours_list:
          temp_hour_name = temp_hour.xpath('.//td[@class="c-location-hours-details-row-day"]/text()').extract_first()
          temp_time_open = temp_hour.xpath('.//td[@class="c-location-hours-details-row-intervals"]//div//span[@class="c-location-hours-details-row-intervals-instance-open"]/text()').extract_first()
          temp_time_close = temp_hour.xpath('.//td[@class="c-location-hours-details-row-intervals"]//div//span[@class="c-location-hours-details-row-intervals-instance-close"]/text()').extract_first()
          temp_time = temp_time_open + ' - ' + temp_time_close + '; '
          temp_hours += temp_hour_name
          temp_hours += temp_time
      item['store_hours'] = temp_hours
      item['coming_soon'] = '0'
      item['country'] = 'United States'

      yield item


  def parse_stores(self, response):
    stores_list = response.xpath('//div[@class="c-location-grid-item"]')

    for store_list in stores_list:
      detail_link = store_list.xpath('.//div[@class="c-location-grid-bottom"]//div[@class="c-location-grid-right"]//div[@class="c-location-grid-item-link-wrapper"]//a[@class="c-location-grid-item-link"]')

      if detail_link:
        temp_url = detail_link.xpath('./@href').extract_first()
        detail_url = self.domain + temp_url[3:]
        request = scrapy.Request(url=detail_url, callback=self.parse_store)
        request.meta['city_url'] = detail_url
        yield request
      else:
        item = ChainItem()
        temp_brand = store_list.xpath('.//div[@class="c-location-grid-top"]//h5[@class="c-location-grid-item-title"]//span[@class="location-name-brand"]/text()').extract_first()
        temp_geo = store_list.xpath('.//div[@class="c-location-grid-top"]//h5[@class="c-location-grid-item-title"]//span[@class="location-name-geo"]/text()').extract_first()
        item['store_name'] = temp_brand + temp_geo
        temp_addr = store_list.xpath('.//div[@class="c-location-grid-bottom"]//div[@class="c-location-grid-left"]//div[@class="c-location-grid-item-address"]//address[@class="c-address"]')
        item['address'] = temp_addr.xpath('.//span[@class="c-address-street"]//span[@class="c-address-street-1"]/text()').extract_first()
        temp_city = temp_addr.xpath('.//span[@class="c-address-city"]//span/text()').extract()
        item['city'] = temp_city[0]
        item['state'] = temp_addr.xpath('.//abbr[@class="c-address-state"]/text()').extract_first()
        item['zip_code'] = temp_addr.xpath('.//span[@class="c-address-postal-code"]/text()').extract_first()
        item['country'] = 'United States'
        item['coming_soon'] = '1'
        item['phone_number'] = store_list.xpath('.//div[@class="c-location-grid-bottom"]//div[@class="c-location-grid-right"]//div[@class="c-location-grid-item-phone"]//div//span/text()').extract_first()
        yield item


  def validate(self, store, property):
    try:
      return store[property]
    except:
      return ""



