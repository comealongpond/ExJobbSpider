import json





class ResultsHandler():
	"""
		Class for handling a results file where
		all the spiders can store their individual results.
		
		results file is thought to be the foundation
		for creating a results template for GUI.
	"""

	results_file_name = 'full_results.json'


	def appendData(self, key, data):
		current_results = {}
		try:
			with open(self.results_file_name, 'r') as f:
				current_results = json.load(f)
		except:
			print('Could not load ' + self.results_file_name)

		current_results[key] = data

		with open(self.results_file_name, 'w') as f:
			json.dump(current_results, f)

	def appendArrayToExistingKey(self, originalkey, newkey, data):
		current_results = {}
		try:
			with open(self.results_file_name, 'r') as f:
				current_results = json.load(f)
		except:
			print('Could not load ' + self.results_file_name)

		if originalkey not in current_results:
			current_results[originalkey] = {}

		current_results[originalkey][newkey] = data

		with open(self.results_file_name, 'w') as f:
			json.dump(current_results, f)
	
	def appendArrayArrayToExistingKey(self, originalkey, newkey, data):
		current_results = {}
		try:
			with open(self.results_file_name, 'r') as f:
				current_results = json.load(f)
		except:
			print('Could not load ' + self.results_file_name)

		if originalkey not in current_results:
			current_results[originalkey] = {}

		try:
			current_results[originalkey][newkey].append(data)
		except:
			current_results[originalkey][newkey] = [data]

		with open(self.results_file_name, 'w') as f:
			json.dump(current_results, f)

	def incrementCounterWithKey(self, key, increment = 1):
		current_results = {}
		try:
			with open(self.results_file_name, 'r') as f:
				current_results = json.load(f)
		except:
			print('Could not load ' + self.results_file_name)

		if key not in current_results:
			current_results[key] = 1
		else:
			current_results[key] = current_results[key] + 1

		with open(self.results_file_name, 'w') as f:
			json.dump(current_results, f)
			
	def appendCookieToExistingKey(self, Spiderkey, data):

		current_results = {}
		try:
			with open(self.results_file_name, 'r') as json_data:
				current_results = json.load(json_data)
		except:
			print('Failed to load ' + self.results_file_name)

		current_results[Spiderkey]['Cookies'].extend(data['Cookies'])
		current_results[Spiderkey]['Grade'] = data['Grade']
		
		with open(self.results_file_name, 'w') as f:
			json.dump(current_results, f)





