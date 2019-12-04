import scrapy
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request

import sys
import json
import configparser

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
#from items import LinkSchemeSpiderItem
from ProgressHandler import ProgressHandler

class LinkSchemeSpider(CrawlSpider):
    name = 'LinkSchemeSpider'
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT' : 2000,
        'CLOSESPIDER_TIMEOUT' : 600,
        'RETRY_ENABLED' : False
    }
    handle_httpstatus_list = [404]




    def __init__(*args, **kwargs):
        #super(LinkSchemeSpider, args[0]).__init__(*args, **kwargs)

        config = configparser.ConfigParser()
        if not config.read('default_settings.ini'):
            raise IOError('cannot load default_settings')

        #Initiate the spider BEFORE starting request
        args[0].http_user = config['DEFAULT']['http_user']
        args[0].http_pass = config['DEFAULT']['http_pass']
        args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
        args[0].start_urls = [config['DEFAULT']['start_url']]
        
        phandler = ProgressHandler()
        phandler.append("Indexing site...")



    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_item)

    def parse_item(self, response):
        print("PARSING ITEM")

        with open('AllUrlLinks.txt', 'a') as f:
            f.write(response.url + '\n')

        already_found_links = []
        try:
            with open('AllUrlLinks.txt', 'r') as f:
                already_found_links = f.readlines()
        except:
            pass
        
        all_links = response.xpath('*//a/@href').extract()
        for link in all_links:
            if link + '\n' in already_found_links:
                    continue
            if link[0] == '/':
                #relative url
                yield Request(self.start_urls[0] + link, callback=self.parse_item)
            elif link[0:4] == 'http' or link[0:3] == 'www':
                 yield Request(link, callback=self.parse_item)


    def closed(self, reason):
        phandler = ProgressHandler()
        if reason == 'finished':
            phandler.append("Successfully indexed site.")
        else: #closespider_timeout
            phandler.append("Stopped indexing site because time limit exceeded.")
