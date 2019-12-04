from .spiders.RefererSpider import RefererSpider
from .spiders.SecurityHeadersSpider import SecurityHeadersSpider
from .spiders.ThirdPartyRequestSpider import ThirdPartyRequestSpider
from .spiders.ThirdPartyCookieSpider import ThirdPartyCookieSpider
from .spiders.RedirectSpider import RedirectSpider
from .spiders.FullSiteSpiders import FullSiteSpiders

from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
import sys
import time
import os
from os import path
import configparser
from urllib.parse import urlsplit

class QuickScanRunner():
	"""
		Class for running the program in default mode.
		i.e when nothing but a single URL is given
	"""

	def run(self, _url):
		start_time = time.time()
		
		runner = CrawlerRunner()

		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		config['DEFAULT']['start_url'] = _url
		config['DEFAULT']['allowed_domain'] = self.getDomainFromUrl(_url)
		config['PROGRESS']['finished'] = '0'
		config['SYSTEM']['runner'] = 'quick'
		
		config['SPIDERS']['FormSpider'] = '0'
		config['SPIDERS']['CookiesSpider'] = '1'
		config['SPIDERS']['ThirdPartyRequestSpider'] = '1'
		config['SPIDERS']['BoxCheckSpider'] == '0'

		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)
			configfile.close()

		@defer.inlineCallbacks
		def crawl():

			yield runner.crawl(RedirectSpider)
			yield runner.crawl(SecurityHeadersSpider)
			yield runner.crawl(RefererSpider)
			yield runner.crawl(FullSiteSpiders, url=_url)

			
			reactor.crash()

			
		crawl()
		reactor.run(installSignalHandlers=False) #The script will block here until done
		
		print("The program took " +  str(round(time.time() - start_time, 2)) + " seconds to run.")

		self.cleanBreak()


	def getDomainFromUrl(self, _url):
		domain =  "{0.netloc}".format(urlsplit(_url))
		if domain[0:4] == 'www.':
			domain = domain[4:]
		"""
		if 'https' in domain[0:5]:
			domain = domain[7:]
		else if 'http' in domain[0:4]:
			domain = domain[6:]
		"""

		return domain

	def cleanBreak(self):
		#Somehow stop reactor here so it can be restarted
		#Avoiding:
		#	Error: Reactor not restartable
		try:
			os.remove('AllUrlLinks.txt')
		except:
			print('Failed to remove file \"AllUrlLinks.txt\"')
			pass
		#Need to also perform a "clean exit"
		#removing tmp files
		print("Program finished")

		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		config['PROGRESS']['finished'] = '1'

		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)
			configfile.close()




