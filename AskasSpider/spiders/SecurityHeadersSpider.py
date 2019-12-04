import scrapy
from scrapy.spiders import Spider, Rule
from scrapy.http import FormRequest
import re
import configparser
import json
import math

from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler


class SecurityHeadersSpider(Spider): #Spider might be better than CrawlSpider
	name = 'SecurityHeadersSpider'

	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = [config['DEFAULT']['start_url']]

	def start_requests(self):
		phandler = ProgressHandler()		
		phandler.append("Getting Security Headers")

		yield scrapy.Request(url=self.start_urls[0], callback=self.parse_i)

	def parse_i(self, response):
		phandler = ProgressHandler()		
		phandler.append("Analysing Security Headers")

		HTTPS = 'https' in response.url[0:5]
		
		results = {}

		results['X-Frame-Options'] = {}
		results['X-XSS-Protection'] = {}
		results['Strict-Transport-Security'] = {}
		results['Content-Security-Policy'] = {}
		results['Server'] = {}
		results['Public-Key-Pins'] = {}
		results['X-Content-Type-Options'] = {}
		results['Referrer-Policy'] = {}
		grade = 0

		try:
			value = response.headers.get("X-Frame-Options").decode("utf-8")
			results['X-Frame-Options']['value'] = value
			
			valueUpper = value.upper()
			if valueUpper == 'SAMEORIGIN':
				results['X-Frame-Options']['status'] = 'good'
				results['X-Frame-Options']['moreinfo'] = 'SameOrigin is a reasonable option. (+15)'
				grade += 15

			elif valueUpper == 'DENY':
				results['X-Frame-Options']['status'] = 'good'
				results['X-Frame-Options']['moreinfo'] = 'Deny is the safest option. (+20)'
				grade += 20
			else:
				results['X-Frame-Options']['status'] = 'warning'
				results['X-Frame-Options']['moreinfo'] = 'This could be dangerous if used carelessly. (+10)'
				grade += 10
		except:
			results['X-Frame-Options']['value'] = 'NOT SET'
			results['X-Frame-Options']['status'] = 'error'
			results['X-Frame-Options']['moreinfo'] = 'X-Frame-Options is a great way to protect users from clickjacking attacks. (+0)'

		results['X-Frame-Options']['readmore'] = 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options'


		try:
			value = response.headers.get("X-XSS-Protection").decode("utf-8")
			results['X-XSS-Protection']['value'] = value

			valueUpper = value.upper()
			if '1; MODE=BLOCK' in valueUpper or '1;MODE=BLOCK' in valueUpper:
				results['X-XSS-Protection']['status'] = 'good'
				results['X-XSS-Protection']['moreinfo'] = 'This the best option. (+20)'
				grade += 20
			else:
				results['X-XSS-Protection']['status'] = 'warning'
				results['X-XSS-Protection']['moreinfo'] = 'This should be nothing other than \"1; mode=block\". (+0)'
		except:
			results['X-XSS-Protection']['value'] = 'NOT SET'
			results['X-XSS-Protection']['status'] = 'error'
			results['X-XSS-Protection']['moreinfo'] = 'X-XSS-Protection is used to activate/configure the browsers built-in reflective XSS protection. (+0)'

		results['X-XSS-Protection']['readmore'] = 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-XSS-Protection'
		
		#Strict-Transport-Security only makes sense for https sites
		if HTTPS:
			try:
				value = response.headers.get("Strict-Transport-Security").decode("utf-8")
				results['Strict-Transport-Security']['value'] = value

				max_age = re.search('max-age=([0-9]+)', str(value))
				max_age = max_age.group(1)
				if int(max_age) < 2592000:
					results['Strict-Transport-Security']['status'] = 'warning'
					results['Strict-Transport-Security']['moreinfo'] = 'max age should be atleast 2592000. (+10)'
					grade += 10
				else:
					results['Strict-Transport-Security']['status'] = 'good'
					results['Strict-Transport-Security']['moreinfo'] = 'This is good. (+20)'
					grade += 20
			except:
				results['Strict-Transport-Security']['value'] = 'NOT SET'
				results['Strict-Transport-Security']['status'] = 'error'
				results['Strict-Transport-Security']['moreinfo'] = 'Strict-Transport-Security is used to tell browsers to only communicate with the server over HTTPS. (+0)'
		else:
			results['Strict-Transport-Security']['value'] = 'NOT SET'
			results['Strict-Transport-Security']['status'] = 'info'
			results['Strict-Transport-Security']['moreinfo'] = 'Strict-Transport-Security is not applicable for HTTP sites. (+0)'

		results['Strict-Transport-Security']['readmore'] = 'https://www.w3.org/TR/CSP2/'

		try:
			value = response.headers.get("Content-Security-Policy").decode("utf-8")
			results['Content-Security-Policy']['value'] = value
			# MORE LOGIC

			results['Content-Security-Policy']['status'] = 'good'
			results['Content-Security-Policy']['moreinfo'] = 'Content-Security-Policy is a good defense against XSS attacks. (+10)'
			grade += 10
		except:
			results['Content-Security-Policy']['value'] = 'NOT SET'
			results['Content-Security-Policy']['status'] = 'error'
			results['Content-Security-Policy']['moreinfo'] = 'Content-Security-Policy is a good defense against XSS attacks. (+0)'

		results['Content-Security-Policy']['readmore'] = 'https://www.w3.org/TR/CSP2/'

		try:
			value = response.headers.get("Server").decode("utf-8")
			results['Server']['value'] = value

			if len(value) > 1:
				results['Server']['status'] = 'warning'
				results['Server']['moreinfo'] = 'Leaking information about the server software might increase vulnerability. (+0)'
			else:
				results['Server']['value'] = 'NOT SET'
				results['Server']['status'] = 'good'
				results['Server']['moreinfo'] = 'Leaking information about the server software might increase vulnerability. (+0)'
		except:
			results['Server']['value'] = 'NOT SET'
			results['Server']['status'] = 'good'
			results['Server']['moreinfo'] = 'Leaking information about the server software might increase vulnerability. (+)'

		results['Server']['readmore'] = 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Server'


		try:
			value = response.headers.get("Public-Key-Pins").decode("utf-8")
			results['Public-Key-Pins']['value'] = value


			results['Public-Key-Pins']['status'] = 'warning'
			results['Public-Key-Pins']['moreinfo'] = 'Public-Key-Pins is complicated to use correctly and can render a site useless if done wrong. (+0)'
		except:
			results['Public-Key-Pins']['value'] = 'NOT SET'
			results['Public-Key-Pins']['status'] = 'good'
			results['Public-Key-Pins']['moreinfo'] = 'Public-Key-Pins is complicated to use correctly and can render a site useless if done wrong. (+5)'
			grade += 5

		results['Public-Key-Pins']['readmore'] = 'https://groups.google.com/a/chromium.org/forum/#!msg/blink-dev/he9tr7p3rZ8/eNMwKPmUBAAJ'


		try:
			value = response.headers.get("X-Content-Type-Options").decode("utf-8")
			results['X-Content-Type-Options']['value'] = value
			# MORE LOGIC

			if value.upper() == 'NOSNIFF':
				results['X-Content-Type-Options']['status'] = 'good'
				results['X-Content-Type-Options']['moreinfo'] = 'This is the only valid option for X-Content-Type-Options. (+20)'
				grade += 20
			else:
				results['X-Content-Type-Options']['status'] = 'error'
				results['X-Content-Type-Options']['moreinfo'] = 'The only valid option for X-Content-Type-Options is nosniff. (+0)'
			
		except:
			results['X-Content-Type-Options']['value'] = 'NOT SET'
			results['X-Content-Type-Options']['status'] = 'error'
			results['X-Content-Type-Options']['moreinfo'] = 'X-Content-Type-Options is essentially a way to opt-out of MIME type sniffing. (+0)'

		results['X-Content-Type-Options']['readmore'] = 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options'


		try:
			results['Referrer-Policy']['value'] = response.headers.get("Referrer-Policy").decode("utf-8")
			# MORE LOGIC

			results['Referrer-Policy']['status'] = 'good'
			results['Referrer-Policy']['moreinfo'] = 'Good. Probably. (+5)'
			grade += 5
		except:
			results['Referrer-Policy']['value'] = 'NOT SET'
			results['Referrer-Policy']['status'] = 'error'
			results['Referrer-Policy']['moreinfo'] = 'This field tells the browser how it should handle referers in requests. (+0)'

		results['Referrer-Policy']['readmore'] = 'https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy'

		results['Grade'] = math.ceil(grade)

		handler = ResultsHandler()
		handler.appendData('SecurityHeadersSpider', results)


	def closed(self, reason):
		phandler = ProgressHandler()
		if reason == 'finished':
			phandler.append("Successfully analysed Security Headers.")
		else:
			phandler.append("Unexpected end of Security Headers analysis - " + reason)



"""
OPEN SOURCE DOMAIN CONNECTION LIST:
https://github.com/disconnectme/disconnect-tracking-protection/blob/master/services.json
"""