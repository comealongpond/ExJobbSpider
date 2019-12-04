import random



EMAIL_DOMAINS = ['yahoo.com', 'gmail.com', 'hotmail.com', 'photonmail.com', 'live.com', 'live.se', 'mail.com']
STREET_DOMAINS = ['Street', 'Drive', 'Walk', 'Way']
class InputGenerator():
	"""
		A class that can generate random values for input fields.

		NOTE: Is not using True Random
	"""

	def generate_email(self, length = 10, domains = [], name = ''):
		"""Generate a random 'valid' email"""

		email_addr = name

		if name == '':
			for i in range(0, length):
				email_addr = email_addr + (chr(random.randint(0, 25) + ord('a')))

		email_addr = email_addr + '@'

		if domains == []:
			global EMAIL_DOMAINS
			return email_addr + EMAIL_DOMAINS[random.randint(0, len(EMAIL_DOMAINS) - 1)]
		else:
			return email_addr + domains[random.randint(0, len(domains) - 1)]


	def generate_username(self, length = 10):
		generated_username = ''

		for i in range(0, length):
			generated_username = generated_username + (chr(random.randint(0, 25) + ord('a')))

		return generated_username


	def generate_phonenumber(self, length = 10):
		"""No global because length should always default to 10"""
		return self.generate_random_number_string(length)


	def generate_password(self, length = 10) :#Needs parameter for requirements on special characters
		generated_password = ''
		for i in range(0, length):
				generated_password = generated_password + (chr(random.randint(0, 25) + ord('a')))
		return generated_password


	def generate_firstname(self): #no length because this is loaded from a dictionary
		"""
		NOTE: Very resource demanding, i.e SLOW 
		"""
		name_caps = ''

		with open('raw_data/firstnames.txt', 'r') as f:
			lines = f.read().splitlines()
			name_caps =random.choice(lines)

		name = name_caps[0]
		for char in name_caps[1:]:
			name = name + char.lower()

		return name
    

	def generate_lastname(self): #no length because this is loaded from a dictionary
		"""
		NOTE: Very resource demanding, i.e SLOW 
		"""
		name_caps = ''

		with open('raw_data/lastnames.txt', 'r') as f:
			lines = f.read().splitlines()
			name_caps =random.choice(lines)

		name = name_caps[0]
		for char in name_caps[1:]:
			name = name + char.lower()

		return name


	def generate_company(self):
		with open('raw_data/companies.txt', 'r') as f:
			lines = f.read().splitlines()
			return random.choice(lines)


	def generate_social(self, length = 10):
		year = random.randint(0, 99) #random year between 1919 and 2018?
		if year < 10:
			year = "0" + str(year)
		else:
			year = str(year)

		month = random.randint(0, 12)
		if month < 10:
			month = "0" + str(month)
		else:
			month = str(month)

		day = random.randint(0, 28)
		if day < 10:
			day = "0" + str(day)
		else:
			day = str(day)
			
		special = self.generate_random_number_string(4)

		return year + month + day + special


	def generate_random_number_string(self, length = 1):
		num = ''

		for i in range(0, length):
			num = num + str(random.randint(0, 9))

		return num


	def generate_address(self, name=''):
		addr_name = name

		if addr_name == '':
			addr_name = self.generate_lastname()

		addr_name = addr_name + STREET_DOMAINS[random.randint(0, len(STREET_DOMAINS) - 1)] + ' ' + self.generate_random_number_string(2)

		return addr_name






