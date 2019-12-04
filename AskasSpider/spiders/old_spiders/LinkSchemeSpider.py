import scrapy
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


import sys
import json
import configparser

from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
#from items import LinkSchemeSpiderItem
from ProgressHandler import ProgressHandler

class LinkSchemeSpider(CrawlSpider):
    name = 'LinkSchemeSpider'
    handle_httpstatus_list = [404]
    rules = (
        Rule(
            LinkExtractor(
                #allow_domains=['api3.cdsuperstore.se'],
                unique=True,
            ),
            follow=True,
            callback='parse_item'
        ),
    )



    def __init__(*args, **kwargs):
        super(LinkSchemeSpider, args[0]).__init__(*args, **kwargs)

        config = configparser.ConfigParser()
        if not config.read('default_settings.ini'):
            raise IOError('cannot load default_settings')

        #Initiate the spider BEFORE starting request
        args[0].http_user = config['DEFAULT']['http_user']
        args[0].http_pass = config['DEFAULT']['http_pass']
        args[0].allowed_domains = [config['DEFAULT']['allowed_domain']]
        args[0].start_urls = [config['DEFAULT']['start_url']]
        
        phandler = ProgressHandler()
        phandler.append("LinkSchemeSpider started")


    def parse_item(self, response):
        with open('AllUrlLinks.txt', 'a') as f:
            f.write(response.url + '\n')


    def closed(self, spider):
        phandler = ProgressHandler()
        phandler.append("LinkSchemeSpider finished")
