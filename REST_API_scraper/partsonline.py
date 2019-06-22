# -*- coding: utf-8 -*-
import scrapy
import json
from Partsonline.items import PartsonlineItem
import math
import pdb


class PartsonlineSpider(scrapy.Spider):

  handle_httpstatus_list = [500, 502]

  name = 'partsonline'
  allowed_domain = 'https://partsonline.mevotech.com'
  
  maker_url = 'https://partsonline.mevotech.com/api/makers/'
  model_url = 'https://partsonline.mevotech.com/api/models/'
  info_url = 'https://partsonline.mevotech.com/api/info/'

  search_url = 'https://partsonline.mevotech.com/api/search/'
  part_url = 'https://partsonline.mevotech.com/api/part/'


  def start_requests(self):

    year = "1973"
    url = self.maker_url + year + '?lang=en'
    param = {
      'year': year
    }
    yield scrapy.Request(url=url, callback=self.parse_Markers, meta=param)


  def parse_Markers(self, response):
    body = json.loads(response.body)
    year = response.meta['year']
    for maker in body['makers']:
      url = self.model_url + year + '/' + maker + '?lang=en'
      param = {
        'year': year,
        'maker': maker
      }
      yield scrapy.Request(url=url, callback=self.parse_Models, meta=param)


  def parse_Models(self, response):
    body = json.loads(response.body)
    year = response.meta['year']
    maker = response.meta['maker']
    for model in body['models']:
      url = self.info_url + year + '/' + maker + '/' + model + '?lang=en'
      param = {
        'year': year,
        'maker': maker,
        'model': model
      }
      yield scrapy.Request(url=url, callback=self.parse_Info, meta=param)



  def parse_Info(self, response):
    if response.status == 500 or response.status == 502:
      print "========================== 500, 502 error ==================="
      pass
    else:
      body = json.loads(response.body)
      year = response.meta['year']
      maker = response.meta['maker']
      model = response.meta['model']
      for external in body['extendedInfo']:
        param = response.meta
        url = self.search_url + year + '/' + maker + '/' + model + '?submodel=' + external['subModel'] + '&drivetype=' + external['driveType'] + '&lang=en'
        yield scrapy.Request(url=url, callback=self.parse_List, meta=param)


  def parse_List(self, response):
    body = json.loads(response.body)

    for category in body:
      for partCategory in category['partCategoryListing']:
        for brand in partCategory['brandData']:
          for part in brand['partListing']:
            param = response.meta
            url = self.part_url + part['partNo'] + '?captcha=null&lang=en'
            yield scrapy.Request(url=url, callback=self.parse_Detail, meta=param)


  def parse_Detail(self, response):
    body = json.loads(response.body)

    item = {}
    item['part_no'] = ""
    item['name'] = ""
    item['details'] = ""
    item['design_type'] = ""
    item['front_Or_Rear_Suspension'] = ""
    item['bearing_type'] = ""
    item['include_hardware'] = ""
    item['pre_Greased'] = ""
    item['grease_Fitting_Included'] = ""
    item['greasable'] = ""
    item['control_Arm_Maximum_Width'] = ""
    item['adjustable'] = ""
    item['ball_joint_included'] = ""
    item['bushings_included'] = ""
    item['control_arm_type'] = ""
    item['material'] = ""
    item['finish'] = ""
    item['bushing_material'] = ""
    item['meets_or_Exceeds_Original_Equipment_Manufacture_Specifications'] = ""
    item['color'] = ""
    item['image1'] = ""
    item['image2'] = ""
    item['image3'] = ""
    item['image4'] = ""
    item['page_url'] = ""
    item['configuration'] = ""
    item['make'] = ""
    item['model'] = ""
    item['position'] = ""
    item['qty'] = ""
    item['application_note'] = ""
    item['year_range'] = ""



    item['part_no'] = body['info']['partNo']
    item['name'] = body['info']['productDescr']

    temp = ""
    for productAttr in body['info']['productAttributes']:
      temp += productAttr['attributeValue'] + " "
    item['details'] = temp

    for productSpec in body['info']['productSpecifications']:

      if productSpec['attributeName'] == 'Design Type':
        item['design_type'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Front Or Rear Suspension':
        item['front_Or_Rear_Suspension'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Bearing Type':
        item['bearing_type'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Includes Hardware':
        item['include_hardware'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Pre Greased':
        item['pre_Greased'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Grease Fitting Included':
        item['grease_Fitting_Included'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Greasable':
        item['greasable'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Control Arm Maximum Width':
        item['control_Arm_Maximum_Width'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Adjustable':
        item['adjustable'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Ball Joint Included':
        item['ball_joint_included'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Bushings Included':
        item['bushings_included'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Control Arm Type':
        item['control_arm_type'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Material':
        item['material'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Finish':
        item['finish'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Bushing Material':
        item['bushing_material'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Meets or Exceeds Original Equipment Manufacture Specifications':
        item['meets_or_Exceeds_Original_Equipment_Manufacture_Specifications'] = productSpec['attributeValue']

      if productSpec['attributeName'] == 'Color':
        item['color'] = productSpec['attributeValue']

    try:
      temp = body['images'][0]
      item['image1'] = temp['assets'][0]['url']
    except:
      item['image1'] = ''

    try:
      temp = body['images'][1]
      item['image2'] = temp['assets'][0]['url']
    except:
      item['image2'] = ''

    try:
      temp = body['images'][2]
      item['image3'] = temp['assets'][0]['url']
    except:
      item['image3'] = ''

    try:
      temp = body['images'][3]
      item['image4'] = temp['assets'][0]['url']
    except:
      item['image4'] = ''

    item['page_url'] = 'https://partsonline.mevotech.com/details/' + body['info']['partNo']

    tempList = []
    try:
      tempList = body['bg']
    except:
      tempList = []

    if len(tempList) > 0:
      for bg in tempList:
        temp = item
        temp['configuration'] = bg['configuration']
        temp['make'] = bg['makeName']
        temp['model'] = bg['modelName']
        temp['position'] = bg['position']
        temp['qty'] = str(bg['qty'])
        temp['application_note'] = bg['vehicleNotes']
        temp['year_range'] = bg['yearRange']
        record = PartsonlineItem()
        record = temp
        yield record
    else:
      temp = item
      record = PartsonlineItem()
      record = temp
      yield record		

