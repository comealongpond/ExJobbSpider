from scrapy.spiders import CrawlSpider
from scrapy.http import FormRequest
import configparser
from subprocess import check_output
from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler
from scrapy.shell import inspect_response
import json

class FormSpider(CrawlSpider):
	name = 'FormSpider'
	
	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = ['http://api3.cdsuperstore.se/shop']

		phandler = ProgressHandler()
		phandler.append("Filling out all forms...")


	def start_requests(self):
		print('1')
		_formdata = {}
		_formdata['altnr'] = '10956211r'
		_formdata['artnr_egenskap'] = '10956213'
		_formdata['Egenskap1'] = 'W31L32'
		_formdata['antal'] = '1'
		_formdata['alt_antal'] = '1'
		_formdata['Ajax'] = 'J'
		_formdata['funk'] = 'laggtill_integrerad_ajax'
		_formdata['artgrp'] = '194'
		_formdata['visa_tillbehor'] = 'true'
		_formdata['tillbehor_visn'] = 'Tillbehor_Varukorg'
		_formdata['tillbehor_sort'] = ''
		_formdata['tillbehor_lista'] = ''
		print('2')
		print(self.start_urls[0])
		yield FormRequest(self.start_urls[0], method= 'POST', callback=self.parse, formdata=_formdata)
		print('3')

	def parse(self, response):
		print('123123')
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		cookies = ""
		for cookie in response.headers.getlist('Set-Cookie'):
			cookies += cookie.decode('utf-8')
			cookies += "---ENDCOOKIE---"
		print(cookies)
		try:
			inspect_response(response, self)
		except Exception as e:
			print(str(e))
		print('jjjklkjluijlkujlkuh')
		try:
			all_cookies = check_output(['./phantomjs', '--cookies-file=cookies.txt', '--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'testt.js', 'http://api3.cdsuperstore.se/cgi-bin/ibutik/AIR_ibutik.fcgi?funk=bestall_steg1', config['DEFAULT']['http_user'], config['DEFAULT']['http_pass'], cookies])
			print(all_cookies)
		except Exception as e:
			print(str(e))
		
