import scrapy
from scrapy.spiders import Spider, Rule
from scrapy.http import FormRequest
import re
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
import configparser
from subprocess import check_output

from ResultsHandler import ResultsHandler
from ProgressHandler import ProgressHandler

class BoxCheckSpider(Spider):

	name = 'BoxCheckSpider'
	
	def __init__(*args, **kwargs):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Initiate the spider BEFORE starting request
		args[0].http_user = config['DEFAULT']['http_user']
		args[0].http_pass = config['DEFAULT']['http_pass']
		args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
		args[0].start_urls = [config['DEFAULT']['start_url']]

		phandler = ProgressHandler()
		phandler.append("BoxCheckSpider started")


	def start_requests(self):
		with open('AllUrlLinks.txt', 'r') as f:
			self.start_urls = f.read().splitlines()
		for _url in self.start_urls:
			if 'http' in _url[0:4]:
				yield scrapy.Request(url=_url, callback=self.parse)


	def parse(self, response):

		selectius = Selector(response)
		if not selectius.xpath('//form//input[contains(@type, "checkbox")]').extract():
			return 

		config = configparser.ConfigParser()
		config.read('default_settings.ini')
		#content = check_output(['./phantomjs','--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'page_wait.js', response.url, config['DEFAULT']['http_user'], config['DEFAULT']['http_pass']])

		#print("\n------- BOXER SPIDER ----------")
		prechecked_boxes_found = []

		#print("Analysing: " + response.url)
		
		hxs = Selector(response)
		boxes_found = hxs.xpath('//input[contains(@type, "checkbox")]').extract()
		found_box = False
		for box in boxes_found:
			if "checked" in box.lower():
				phandler = ProgressHandler()
				phandler.append("BoxCheckSpider found a prechecked box at: <span class=\"italicized\">" + response.url + "</span>")
				prechecked_boxes_found.append(box)
				found_box = True

		if found_box:
			handler = ResultsHandler()
			handler.appendArrayToExistingKey('BoxCheckSpider', response.url, prechecked_boxes_found)
		#if not found_box:
			#print("Found no prechecked box.")

		#print("-------------------------------\n")
	
	def closed(self, spider):
		phandler = ProgressHandler()
		phandler.append("BoxCheckSpider finished")

