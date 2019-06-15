# -*- coding: utf-8 -*-
import scrapy
import json
from Sourcing.items import SourcingItem
import math
import pdb



class Sourcing1Spider(scrapy.Spider):

	name="sourcing1"

	start_url = "https://sourcing.io/"
	login_url = "https://sourcing.io/login"
	index_url = "https://sourcing.io/search"
	search_url = "https://sourcing.io/v1/people/search"

	def start_requests(self):
		url = self.login_url
		formdata = {
			"email": "gregory.herbe@nexten.io",
			"password": "lifeisgood2018;"
		}
		yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, callback=self.startSearch)


	def startSearch(self, response):
		url = self.index_url
		yield scrapy.Request(url=url, callback=self.startParse)


	def startParse(self, response):
		url = self.search_url
		header = {
			":authority": "sourcing.io",
			":method": "POST",
			":path": "/v1/people/search",
			":scheme": "https"
		}
		formdata = {
			"offset": "0",
			"order": "desc",
			"sort": "_score"
		}
		param = {
			"index": 0
		}
		yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, headers=header, meta=param, callback=self.parseList)


	def parseList(self, response):
		body = json.loads(response.body)
		try:
			for user in body['items']:
				item = SourcingItem()
				try:
					item['assigned_user'] = user['assigned_user']
				except:
					item['assigned_user'] = ""

				try:
					item['all_languages'] = user['all_languages']
				except:
					item['all_languages'] = ""

				try:
					item['avatar_url'] = user['avatar_url_260']
				except:
					item['avatar_url'] = ""

				try:
					item['bio'] = user['bio']
				except:
					item['bio'] = ""

				try:
					item['company_name'] = user['company_name']
				except:
					item['company_name'] = ""

				try:
					item['connected'] = user['connected']
				except:
					item['connected'] = ""

				try:
					item['educations'] = user['educations']
				except:
					item['educations'] = ""

				try:
					item['email'] = user['email']
				except:
					item['email'] = ""

				try:
					item['facebook'] = user['facebook']
				except:
					item['facebook'] = ""

				try:
					item['favorite'] = user['favorite']
				except:
					item['favorite'] = ""

				try:
					item['favourited_users'] = user['favourited_users']
				except:
					item['favourited_users'] = ""

				try:
					item['first_name'] = user['first_name']
				except:
					item['first_name'] = ""

				try:
					item['frameworks'] = user['frameworks']
				except:
					item['frameworks'] = ""

				try:	
					item['gems_count'] = user['gems_count']
				except:
					item['gems_count'] = ""

				try:
					item['geocode_city'] = user['geocode_city']
				except:
					item['geocode_city'] = ""

				try:
					item['geocode_country'] = user['geocode_country']
				except:
					item['geocode_country'] = ""

				try:
					item['geocode_state'] = user['geocode_state']
				except:
					item['geocode_state'] = ""

				try:
					item['github'] = user['github']
				except:
					item['github'] = ""

				try:
					item['github_created'] = user['github_created']
				except:
					item['github_created'] = ""

				try:
					item['github_followers_count'] = user['github_followers_count']
				except:
					item['github_followers_count'] = ""

				try:
					item['github_hireable'] = user['github_hireable']
				except:
					item['github_hireable'] = ""

				try:
					item['github_updated'] = user['github_updated']
				except:
					item['github_updated'] = ""

				try:
					item['gravatar_id'] = user['gravatar_id']
				except:
					item['gravatar_id'] = ""

				try:
					item['headline'] = user['headline']
				except:
					item['headline'] = ""

				try:
					item['hidden'] = user['hidden']
				except:
					item['hidden'] = ""

				try:
					item['hireable'] = user['hireable']
				except:
					item['hireable'] = ""

				try:
					item['Id'] = user['id']
				except:
					item['Id'] = ""

				try:
					item['languages'] = user['languages']
				except:
					item['languages'] = ""

				try:
					item['last_name'] = user['last_name']
				except:
					item['last_name'] = ""

				try:
					item['linkedin'] = user['linkedin']
				except:
					item['linkedin'] = ""

				try:
					item['linkedin_users'] = user['linkedin_users']
				except:
					item['linkedin_users'] = ""

				try:
					item['location'] = user['location']
				except:
					item['location'] = ""

				try:
					item['name'] = user['name']
				except:
					item['name'] = ""

				try:
					item['packages_count'] = user['packages_count']
				except:
					item['packages_count'] = ""

				try:
					item['score'] = user['score']
				except:
					item['score'] = ""

				try:
					item['slug'] = user['slug']
				except:
					item['slug'] = ""

				try:
					item['state'] = user['state']
				except:
					item['state'] = ""

				try:
					item['title'] = user['title']
				except:
					item['title'] = ""

				try:
					item['twitter'] = user['twitter']
				except:
					item['twitter'] = ""

				try:
					item['twitter_connected'] = user['twitter_connected']
				except:
					item['twitter_connected'] = ""

				try:
					item['twitter_follower_users'] = user['twitter_follower_users']
				except:
					item['twitter_follower_users'] = ""

				try:
					item['twitter_followers_count'] = user['twitter_followers_count']
				except:
					item['twitter_followers_count'] = ""

				try:
					item['twitter_following_users'] = user['twitter_following_users']
				except:
					item['twitter_following_users'] = ""

				try:
					item['twitter_id'] = user['twitter_id']
				except:
					item['twitter_id'] = ""

				try:
					item['twitter_mutual_users'] = user['twitter_mutual_users']
				except:
					item['twitter_mutual_users'] = ""

				try:
					item['url'] = user['url']
				except:
					item['url'] = ""

				yield item
		except:
			print "===================== error ========================"
			pass

		index = response.meta['index']
		index = index + 20
		if index <= 1000000:
			url = self.search_url
			header = {
				":authority": "sourcing.io",
				":method": "POST",
				":path": "/v1/people/search",
				":scheme": "https"
			}
			formdata = {
				"offset": str(index),
				"order": "desc",
				"sort": "_score"
			}
			param = {
				"index": index
			}
			yield scrapy.FormRequest(url=url, method="POST", formdata=formdata, headers=header, meta=param, callback=self.parseList)

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