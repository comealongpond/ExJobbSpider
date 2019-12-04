from .spiders.RefererSpider import RefererSpider
from .spiders.SecurityHeadersSpider import SecurityHeadersSpider
from .spiders.ThirdPartyRequestSpider import ThirdPartyRequestSpider
from .spiders.RedirectSpider import RedirectSpider
from .spiders.ThirdPartyCookieSpider import ThirdPartyCookieSpider
from .spiders.FullSiteSpiders import FullSiteSpiders
from .spiders.LinkSchemeSpider import LinkSchemeSpider
from twisted.internet import reactor, defer
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from scrapy.settings import Settings
from scrapy.crawler import CrawlerRunner
import sys
import time
import os
from os import path
import configparser
from urllib.parse import urlsplit
from scrapy.utils.project import get_project_settings

class AdvancedRunner():

	settings = None
	
	def __init__(self, _settings):
		self.settings = _settings;
		return

	def run(self, _url):
		#Clear previous results
		#Only when testing.
		#The results should be cleared differently in prod
		try:
			os.remove("full_results.json")
			os.remove("cookies.txt")
		except OSError:
			print('Failed to remove file \"full_results.json\"')
			pass

		#Create file ????
		open("full_results.json", "a").close()

		start_time = time.time()
		
		try:
			#settings = get_project_settings()
			configure_logging()
			runner = CrawlerRunner(self.settings)
		except Exception as e:
			print("CrawlerRunner init failed - " + str(e))


		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		config['DEFAULT']['start_url'] = _url
		config['PROGRESS']['finished'] = '0'
		config['SYSTEM']['runner'] = 'advanced'

		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)
			configfile.close()

		try:
			@defer.inlineCallbacks
			def crawl():
				yield runner.crawl(LinkSchemeSpider)

				if config['SPIDERS']['RedirectSpider'] == '1':
					yield runner.crawl(RedirectSpider)

				if config['SPIDERS']['SecurityHeadersSpider'] == '1':
					yield runner.crawl(SecurityHeadersSpider)

				if config['SPIDERS']['CookiesSpider'] == '1' or config['SPIDERS']['FormSpider'] == '1' or config['SPIDERS']['BoxCheckSpider'] == '1' or config['SPIDERS']['ThirdPartyRequestSpider'] == '1':
					try:
						with open("AllUrlLinks.txt", "r") as f:
							for link in f.readlines():
								yield runner.crawl(FullSiteSpiders, url = link.replace("\n", ""))
					except Exception as e:
						print("LinkSchemeSpider did nothin. -> " + str(e))


				
				reactor.crash()

				
			crawl()
			reactor.run(installSignalHandlers=False) #The script will block here until done
			
			print("The program took " +  str(round(time.time() - start_time, 2)) + " seconds to run.")

			self.cleanBreak()
		except Exception as e:
			print("running reactor failed - " + str(e))




	def cleanBreak(self):
		#Somehow stop reactor here so it can be restarted
		#Avoiding:
		#	Error: Reactor not restartable

		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		try:
			if config['PROGRESS']['finished'] == 'interrupted':
				#GUI_Test will handle cleanup if interrupted
				return
		except:
			pass


		"""
			TODO: Move to a separate class like CleanupCrew or smth
		"""
		#Remove all the tmp files used during the run
		#username.txt, mail.txt, firstname.txt, lastname.txt, address.txt, phone.txt, forms_sent.txt, forms.txt
		try:
			os.remove("AllUrlLinks.txt")
		except OSError:
			print('Failed to remove file \"AllUrlLinks.txt\"')
			pass

		try:
			os.remove("username.txt")
		except OSError:
			print('Failed to remove file \"username.txt"')
			pass

		try:
			os.remove("mail.txt")
		except OSError:
			print('Failed to remove file \"mail.txt\"')
			pass

		try:
			os.remove("firstname.txt")
		except OSError:
			print('Failed to remove file \"firstname.txt\"')
			pass

		try:
			os.remove("lastname.txt")
		except OSError:
			print('Failed to remove file \"lastname.txt\"')
			pass

		try:
			os.remove("address.txt")
		except OSError:
			print('Failed to remove file \"address.txt\"')
			pass

		try:
			os.remove("phone.txt")
		except OSError:
			print('Failed to remove file \"phone.txt\"')
			pass

		try:
			os.remove("forms_sent.txt")
		except OSError:
			print('Failed to remove file \"forms_sent.txt\"')
			pass

		try:
			os.remove("forms.txt")
		except OSError:
			print('Failed to remove file \"forms.txt\"')
			pass

		try:
			os.remove("zipcode.txt")
		except OSError:
			print('Failed to remove file \"zipcode.txt\"')
			pass

		try:
			os.remove("country.txt")
		except OSError:
			print('Failed to remove file \"country.txt\"')
			pass

		try:
			os.remove("city.txt")
		except OSError:
			print('Failed to remove file \"city.txt\"')
			pass

		try:
			os.remove("social.txt")
		except OSError:
			print('Failed to remove file \"social.txt\"')
			pass

		try:
			os.remove("company.txt")
		except OSError:
			print('Failed to remove file \"social.txt\"')
			pass

		print("Program finished")

		config['PROGRESS']['finished'] = '1'

		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)
			configfile.close()