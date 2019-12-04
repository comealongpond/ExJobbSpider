import outputmenu
import configparser

class MenuHandler():
	spider_dictionary = {'1' : 'SecurityHeadersSpider', '2': 'LoginSpider', '3' : 'RegisterSpider', '4' : 'BoxCheckSpider', '5' : 'ThirdPartyCookieSpider', '6' : 'ThirdPartyRequestSpider', '7' : 'LinkSchemeSpider', '8' : 'RefererSpider'}
	spiders_to_run = []
	def run(self):
		outputmenu.print_title()
		outputmenu.print_menu()
		config = configparser.ConfigParser()
		config.read('default_settings.ini')
		configChanged = False
		while True:
			if configChanged:
				with open('default_settings.ini', 'w') as configfile:
					config.write(configfile)

			choice = input('-> ')
			if choice == 'q':
				return []
			
			if choice == 'r':
				if self.settings_good_enough_to_run():
					print("Spiders initialized!")
					return self.spiders_to_run
				else:
					print("You must give better settings before running.")
					continue
				
			if choice == 'm':
				outputmenu.print_menu()
				continue
			
			if choice == 'h':
				#output.print HELP MENU
				continue
			
			if choice == 'd':
				#set allowed domain
				#more validation lol
				config['DEFAULT']['allowed_domain'] = input('DOMAIN: ')
				configChanged = True
				#askasspidersettings.default_allowed_domains = [input('DOMAIN: ')]
				continue

			if choice == 's':
				#set start url
				#more validation lol
				config['DEFAULT']['start_url'] = input('URL: ')
				configChanged = True
				#askasspidersettings.default_start_urls = [input('URL: ')]
				continue

			if choice == 'u':
				#set http user
				#more validation lol
				config['DEFAULT']['http_user'] = input('username: ')
				configChanged = True
				#askasspidersettings.default_http_user = input('username: ')
				continue

			if choice == 'p':
				#set http password
				#more validation lol
				config['DEFAULT']['http_pass'] = input('password: ')
				configChanged = True
				#askasspidersettings.default_http_pass = input('password: ')
				continue

			if choice == 'v':
				#view settings
				self.print_settings()
				continue

			if choice == 'l':
				self.print_choosen_spiders()
				continue

			if self.validate_input(choice):
				self.spiders_to_run.append(self.spider_dictionary[choice])
				self.print_choosen_spiders()
			
	def validate_input(self, choice):
		if choice not in self.spider_dictionary.keys():
			print("Bad input!")
			return False
		if self.spider_dictionary[choice] in self.spiders_to_run:
			print("Spider already in queue!")
			return False
		return True

	def print_choosen_spiders(self):
		print('\nSpiders in queue:')
		print('-----------------')
		
		for i in range(0, len(self.spiders_to_run)):
			print(str(i+1) + '. ' + self.spiders_to_run[i])
		
		print('-----------------\n')

	def print_settings(self):
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		"""
		TODO:
			Most likely there is a much better option for displaying
			the config file contents. like config.print() or smth
		"""
		print('\n____SETTINGS____')

		for key in config['DEFAULT']:
			print(key + ' : ' + config['DEFAULT'][key])

		print('________________\n')


	def settings_good_enough_to_run(self):
		#Check if settings are setup before running
		try:
			#Is this all thats needed to run?
			config = configparser.ConfigParser()
			config.read('default_settings.ini')
			test_domain = config['DEFAULT']['allowed_domain']
			test_url = config['DEFAULT']['start_url']

		except:
			return False

		return True






