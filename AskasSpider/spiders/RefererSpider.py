import scrapy
from scrapy.spiders import Spider
from subprocess import check_output
import configparser
import json
from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler
from urllib.parse import urlparse
from urllib.parse import urlsplit

class RefererSpider(Spider):
	name = 'RefererSpider'

	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = [config['DEFAULT']['start_url']]

	def start_request(self):
		

		yield scrapy.Request(self.start_urls[0], callback=self.parse, dont_filer=True)

	def parse(self, response):

		phandler = ProgressHandler()
		phandler.append("Analising referers...")
		results = {'Policy': '', 'Status': '', 'Info': ''}

		try:
			results['Policy'] = response.headers.get("Referrer-Policy").decode("utf-8")
		except:
			results['Policy'] = 'NOT SET'

		if results['Policy'] == 'no-referrer':
			results['Status'] = 'good'
			results['Info'] = 'No referers leaked! The Referer header will be omitted entirely. No referrer information is sent along with requests'

		if results['Policy'] == 'no-referrer-when-downgrade':
			results['Status'] = 'error'
			results['Info'] = 'Referers could be leaked! This is the user agent default behavior if no policy is specified. The URL is sent as a referer when the protocol security level stays the same (HTTPS->HTTPS), but not when sent from HTTPS to HTTP.'

		if results['Policy'] == 'origin':
			results['Status'] = 'warning'
			results['Info'] = 'Referers is leaked... However, only the domain name is sent as a referer in all cases which COULD be sensitive data but in most cases not.'

		if results['Policy'] == 'origin-when-cross-origin':
			results['Status'] = 'warning'
			results['Info'] = 'Sends the full URL as referer when performing requests to the same origin, but only sends the domin name when performing requests to other sites.'


		if results['Policy'] == 'same-origin':
			results['Status'] = 'good'
			results['Info'] = 'A referrer will be sent for requests to the same origin, but any requests to other origins will contain no referrer information'

		if results['Policy'] == 'strict-origin':
			results['Status'] = 'warning'
			results['Info'] = 'No referer is sent when sending requests from HTTPS to HTTP. Only the domain is sent as referrer when the protocol security level is the same (HTTPS->HTTPS) or (HTTP->HTTP).'		

		if results['Policy'] == 'strict-origin-when-cross-origin':
			results['Status'] = 'warning'
			results['Info'] = 'Sends a full URL when performing a same-origin requests but only sends the origin of the document when the protocol security level is HTTPS to HTTPS. Does not send a referrer to a less secure destination (HTTPS->HTTP).'

		if results['Policy'] == 'unsafe-url':
			results['Status'] = 'error'
			results['Info'] = 'Referers leaked!! Sends the full URL when performing either same-origin or cross-origin requests. '

		if results['Policy'] == 'NOT SET':
			results['Status'] = 'error'
			results['Info'] = 'Referers leaked! A Referrer-Policy should be set to prevent sensitive data from leaking'

		handler = ResultsHandler()
		handler.appendData('RefererSpider', results)




