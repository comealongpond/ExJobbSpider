import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import FormRequest


#FOR SOME REASON THIS IS THE ONLY WAY TO IMPORT INPUTGENERATOR CONSISTENTLY
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from InputGenerator import InputGenerator
from ProgressHandler import ProgressHandler
#from items import RegisterSpiderItem

class RegisterSpider(CrawlSpider):
	""" Registrera """
	name = 'RegisterSpider'
	http_user = 'erik'
	http_pass = 'lindow'
	allowed_domains = ['api3.cdsuperstore.se']
	start_urls = ['http://api3.cdsuperstore.se/cgi-bin/ibutik/AIR_ibutik.fcgi?funk=kund_ny&nastasteg=kundlogin&Spara_Losen=Y&anvnamn=&funk2=dinsida&stegtre=0']
	formdata = {'funk' : 'kund_ny_slutfor', 'nastasteg' : 'kundlogin', 'Pnr' : '', 'Fornamn' : '', 'Efternamn' : '', 'Anvnamn' : '', 'Losenord' : '', 'Losenord_Repeterat' : '', 'Adress' : '', 'Postnr' : '12345', 'Ort' : '', 'Land' : '', 'Epost' : '', 'Tel_Mobil' : '', 'AIR-EverythingInItsRightPlace' : 'AIR'}
	
	def start_requests(self):
		phandler = ProgressHandler()
		phandler.append("RegisterSpider started")

		ipg = InputGenerator()
		
		self.formdata['Adress'] = ipg.generate_address()
		self.formdata['Tel_Mobil'] = ipg.generate_phonenumber()
		self.formdata['Pnr'] = ipg.generate_phonenumber() # could be its own generator
		self.formdata['Fornamn'] = ipg.generate_firstname()
		self.formdata['Efternamn'] = ipg.generate_lastname()
		self.formdata['Epost'] = ipg.generate_email(name = self.formdata['Fornamn'].lower() + '.' + self.formdata['Efternamn'].lower())
		self.formdata['Anvnamn'] = self.formdata['Fornamn'].lower() + ipg.generate_random_number_string(length = 4)

		pwd = ipg.generate_password()
		self.formdata['Losenord'] = pwd
		self.formdata['Losenord_Repeterat'] = pwd

		yield FormRequest(self.start_urls[0], method = 'POST', callback=self.parse_item, formdata=self.formdata)

	def parse_item(self, response):
		phandler = ProgressHandler()
		phandler.append("RegisterSpider running")

		with open('login.json', 'w') as f:
			f.write('{"username" : \"' + self.formdata['Anvnamn'] + '\", "password" : \"' + self.formdata['Losenord'] + '\"}')
		#item = RegisterSpiderItem()
		#item['username'] = self.formdata['Anvnamn']
		#item['password'] = self.formdata['Losenord']
		#item['email'] = self.formdata['Epost']
		
		
		print('\n\n<<<< Skapade ett konto >>>>>>')
		print('Fornamn:   ' + self.formdata['Fornamn'])
		print('Efternamn: ' + self.formdata['Efternamn'])
		print('Pnr:       ' + self.formdata['Pnr'])
		print('Tel_Mobil: ' + self.formdata['Tel_Mobil'])
		print('Adress:    ' + self.formdata['Adress'])
		print('Anvnamn:   ' + self.formdata['Anvnamn'])
		print('Epost:     ' + self.formdata['Epost'])
		print('Losenord:  ' + self.formdata['Losenord'])
		print('<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>\n\n')

		phandler.append("RegisterSpider finished")

		#return item
