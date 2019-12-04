import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import FormRequest
import json
import os

from ProgressHandler import ProgressHandler

"""
THIS IS NOT WORKING DONT RUN THIS SPIDER
"""


class LoginSpider(CrawlSpider):

	name = 'LoginSpider'
	http_user = 'erik'
	http_pass = 'lindow'
	allowed_domains = ['api3.cdsuperstore.se']
	start_urls = ['http://api3.cdsuperstore.se/cgi-bin/ibutik/AIR_ibutik.pl']
	formdata = {'Anvnamn' : '', 'Losenord' : '', 'funk' : 'kundlogin_slutfor', 'anvnamn' : '', 'stegtre' : '0', 'funk2' : 'dinsida', 'Spara_Losen' : 'Y'}

	def start_requests(self):
		phandler = ProgressHandler()
		phandler.append("LoginSpider started")

		try:
			login_data = json.load(open('login.json'))
			self.formdata['Anvnamn'] = login_data["username"]
			self.formdata['Losenord'] = login_data["password"]
			
		except FileNotFoundError:
			print("\nWARNING: Failed to load login data.\n")
			print("Please enter login information manually:")
			self.formdata['Anvnamn'] = input("username: ")
			self.formdata['Losenord'] = input("password: ")
			print("Thanks!")

		yield FormRequest(self.start_urls[0], method = 'POST', callback=self.parse, formdata=self.formdata)

	def parse(self, response):
		phandler = ProgressHandler()
		phandler.append("LoginSpider running")

		Cookies = str(response.headers.getlist('Set-Cookie'))
		if 'IBUTA=;' not in Cookies and 'IBUTA=0' not in Cookies:
		#if response.url == 'http://api3.cdsuperstore.se/cgi-bin/ibutik/AIR_ibutik.pl':
			print("\n\n\n*********************************\nLOGGED IN " + self.formdata['Anvnamn'] + "\n*********************************\n\n\n")
		else:
			print("\n\n\n*********************************\nFAILED TO LOG IN " + self.formdata['Anvnamn'] + "\n*********************************\n\n\n")

		phandler.append("LoginSpider finished")
