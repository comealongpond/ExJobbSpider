import scrapy
from scrapy.spiders import CrawlSpider
from subprocess import check_output
import configparser
import json
import math

from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler

class ThirdPartyCookieSpider(CrawlSpider):
	name = 'ThirdPartyCookieSpider'

	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = [config['DEFAULT']['start_url']]

	def start_request(self):
		yield scrapy.FormRequest(self.start_urls[0], callback=self.parse, dont_filer=True)

	def parse(self, response):
		phandler = ProgressHandler()
		#phandler.append('Analysing cookies <span class="animated-dots"><div></div><div></div><div></div> </span>' , newline = False)
		phandler.append('Analysing cookies...')
		config = configparser.ConfigParser()
		config.read('default_settings.ini')
		

		#print(config['DEFAULT']['http_user'] + config['DEFAULT']['http_pass'])
		print('Analyzing cookies...')
		all_cookies = check_output(['./phantomjs','--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'read_cookies.js', self.start_urls[0], config['DEFAULT']['http_user'], config['DEFAULT']['http_pass']])
		all_cookies = self.striptease(all_cookies)

		with open('all_cookies.json', 'w') as f:
			f.write(all_cookies)

		print('---------------------------------')
		print('Cookies saved in all_cookies.json')
		print('---------------------------------')

		jsonCookieObject = json.loads(all_cookies)
		firstpartycookies = {'Cookies': [], 'Grade': 0}
		thirdpartycookies = {'Cookies': [], 'Grade': 0}
		firstpartycookie_grade = 0
		thirdpartycookie_grade = 0
		for cookie in jsonCookieObject:
			if config['DEFAULT']['allowed_domain'] not in cookie['domain']:
				thirdpartycookies['Cookies'].append(cookie)
			else:
				firstpartycookies['Cookies'].append(cookie)

	
		for cookie2 in firstpartycookies['Cookies']:
			if cookie2['httponly']:
				firstpartycookie_grade += 50
			if cookie2['secure']:
				firstpartycookie_grade += 50

		try:
			firstpartycookie_grade = math.ceil(firstpartycookie_grade / len(firstpartycookies['Cookies']))
			firstpartycookies['Grade'] = firstpartycookie_grade
		except:
			print('no first party cookies')
			firstpartycookies['Grade'] = 'N/A'
		

		for cookie3 in thirdpartycookies['Cookies']:
			if cookie3['httponly']:
				thirdpartycookie_grade += 50
			if cookie3['secure']:
				thirdpartycookie_grade += 50
		
		try:
			thirdpartycookie_grade = math.ceil(thirdpartycookie_grade / len(thirdpartycookies['Cookies']))
			thirdpartycookies['Grade'] = thirdpartycookie_grade
		except:
			print('no third party cookies')
			thirdpartycookies['Grade'] = 'N/A'

		handler = ResultsHandler()
		handler.appendData('FirstPartyCookies', firstpartycookies)
		handler.appendData('ThirdPartyCookies', thirdpartycookies)
		phandler.append("Analysing cookies finished!")

	def striptease(self, data):
		s = data.decode('utf-8')
		try:
			index = s.find("[")
			return s[index:]
		except Exception as e:
			print(str(e))
			return "[]"





			
			