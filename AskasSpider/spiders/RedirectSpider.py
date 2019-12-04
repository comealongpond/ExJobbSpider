import scrapy
from scrapy.spiders import Spider, Rule
import configparser
from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler
from scrapy.shell import inspect_response

class RedirectSpider(Spider): #Spider might be better than CrawlSpider
	name = 'RedirectSpider'

	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = [config['DEFAULT']['start_url']]

	def start_requests(self):
		yield scrapy.Request(url=self.start_urls[0], callback=self.parse)

	def parse(self, response):
		phandler = ProgressHandler()
		#phandler.append('Checking for redirects <span class="animated-dots"><div></div><div></div><div></div> </span>' , newline = False)
		phandler.append('Analysing redirects...')
		#inspect_response(response, self)
		results = {}
		redirect_urls = []
		try:
			for url in response.request.meta.get('redirect_urls'):
				redirect_urls.append(url)
			redirect_urls.append(response.url)
		except:
			redirect_urls = []

		if not redirect_urls:
			results['redirect_urls'] = 'Did not Redirect!'
			results['number_of_redirects'] = '0'
		else:
			results['redirected_urls'] = redirect_urls
			try:
				results['number_of_redirects'] = response.request.meta.get('redirect_times')
			except:
				results['number_of_redirects'] = '0'

	
		if response.url.startswith('https'):
			results['https_as_default'] = True
			results['Grade'] = 100
		else:
			results['https_as_default'] = False
			results['Grade'] = 0

			

		handler = ResultsHandler()
		handler.appendData('RedirectSpider', results)

		phandler.append("Analysing redirects finished!")
		
		print("\nINFO: RedirectSpider finished.")