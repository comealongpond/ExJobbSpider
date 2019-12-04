import scrapy
from scrapy.spiders import CrawlSpider
from subprocess import check_output
import configparser
import json

from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler

class ThirdPartyRequestSpider(CrawlSpider):
	name = 'ThirdPartyRequestSpider'

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
		phandler.append("Analysing thirdpartyrequests...")

		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		all_requests = check_output(['./phantomjs','--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'read_thirdpartyrequests.js', self.start_urls[0], config['DEFAULT']['http_user'], config['DEFAULT']['http_pass']])
		
		thirdpartyrequests = []
		with open('all_requests.txt', 'wb') as f:
			f.write(all_requests)


		with open('all_requests.txt') as f:
			for line in f:
				spltAr = line.split("://")
				i = (0,1)[len(spltAr)>1]
				domain = spltAr[i].split("?")[0].split('/')[0].split(':')[0].lower();
				
				if config['DEFAULT']['allowed_domain'] not in domain:
					#HANTERA HTTP://:0/
					if domain not in thirdpartyrequests:
						thirdpartyrequests.append(domain)
					
		
		if not thirdpartyrequests:
			print('\n*****************************************\n')
			print("No thirdpartyrequests were found!")
			print('\n*****************************************\n')
		else:
			print('\n*****************************************\n')
			print(str(len(thirdpartyrequests)) + ' unique thirdpartyrequests were found: \n')
			for requests in thirdpartyrequests:
				print(requests)

			handler = ResultsHandler()
			handler.appendData('ThirdPartyRequestSpider', thirdpartyrequests)
			
			print('\n*****************************************\n')

			phandler.append("Analysing thirdpartyrequests finished!")


		