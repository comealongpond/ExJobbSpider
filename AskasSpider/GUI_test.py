import json
import configparser
import os
import time
import _thread
import math

from scrapy.utils.project import get_project_settings

from twisted.internet import reactor

from multiprocessing import Pool

from jinja2 import Environment
from jinja2.loaders import FileSystemLoader

from . import DefaultRunner
from . import QuickScanRunner
from . import AdvancedRunner

from flask import *

app = Flask(__name__)
app.debug = True


def check_http_in_url(url):
	if not url.startswith('http'):
		url = ''.join(('http://', url))
	if url.startswith('https'):
		url = url.replace('https', 'http')
	return url


@app.route("/")
def hello():
	config = configparser.ConfigParser()
	config.read('default_settings.ini')

	return render_template('index.html')

@app.route('/run_advanced', methods=['POST'])
def run_advanced():
	if request.method == 'POST':
		try:
			#Get the config file and set up the sections
			config = configparser.ConfigParser()
			config.read('default_settings.ini')

			#Section setup (fail-safe since this should already have happened on previous program exit)
			config['DEFAULT'] = {}
			config['SYSTEM'] = {}
			config['PROGRESS'] = {}
			config['OPTIONAL'] = {}
			config['SPIDERS'] = {}

			request_string = request.get_data().decode('utf8')

			config['DEFAULT']['allowed_domain'] = request.form['allowed-domain']
			#This must be set after url is retrieved
			#config['DEFAULT']['start_url'] = request.form['front-page-url']
			config['DEFAULT']['http_user'] = request.form['http-user']
			config['DEFAULT']['http_pass'] = request.form['http-pass']

			if request.form.get('post_forms'):
				config['SPIDERS']['FormSpider'] = '1'
			else:
				config['SPIDERS']['FormSpider'] = '0'

			if request.form.get('scan_for_cookies'):
				config['SPIDERS']['CookiesSpider'] = '1'
			else:
				config['SPIDERS']['CookiesSpider'] = '0'

			if request.form.get('check_security_headers'):
				config['SPIDERS']['SecurityHeadersSpider'] = '1'
			else:
				config['SPIDERS']['SecurityHeadersSpider'] = '0'

			if request.form.get('check_https'):
				config['SPIDERS']['RedirectSpider'] = '1'
			else:
				config['SPIDERS']['RedirectSpider'] = '0'

			if request.form.get('check_prechecked_boxes'):
				config['SPIDERS']['BoxCheckSpider'] = '1'
			else:
				config['SPIDERS']['BoxCheckSpider'] = '0'

			if request.form.get('scan_thirdparty_requests'):
				config['SPIDERS']['ThirdPartyRequestSpider'] = '1'
			else:
				config['SPIDERS']['ThirdPartyRequestSpider'] = '0'

			""" Not Implemented Yet
			config['DEFAULT']['login_action_url'] = request.form['login-action-url']
			config['DEFAULT']['login_username'] = request.form['login-username']
			config['DEFAULT']['login_password'] = request.form['login-password']
			config['DEFAULT']['register_action_url'] = request.form['register-action-url']
			config['DEFAULT']['register_username'] = request.form['register-username']
			config['DEFAULT']['register_password'] = request.form['register-password']
			"""

		except Exception as e:
			return render_template('index.html', errormsg = "Could not get the form data. Error: " + str(e))
		

		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)

		#Initiate the runner and get project settings
		try:
			runner = AdvancedRunner.AdvancedRunner(get_project_settings())
		except Exception as e:
			return render_template('index.html', errormsg = "Failed to load runner settings. Error: " + str(e))

		try:
			#Get the given url
			url = check_http_in_url(request.form['front-page-url'])
			
			#Start the runner in a new thread so the UI doesn't lock
			_thread.start_new_thread(runner.run, (url,))

			#Go to the progress page
			return redirect('/yield')

		except Exception as e:
			return render_template('index.html', errormsg = "Failed to create new thread for runner. Error: " + str(e))


	#If someone tries this url randomly, just return to front page
	return render_template('index.html')


#TESTING OUTPUT STREAMING
@app.route('/yield')
def index(): #Cuz 'yield' is a keyword
	#TODO: Do something to redirect user to startpage
	#if coming here without actually running a program
	#for instance when a user clicks "back" on results page

	#if we load this template normally instead we can send along some data
	#like which runner is running, which url is being analysed, etc
	#and display on yield page
	env = Environment(loader=FileSystemLoader('templates'))
	tmpl = env.get_template('result.html')

	return Response(tmpl.generate())


@app.route('/get_progress')
def get_progress():
	config = configparser.ConfigParser()
	config.read('default_settings.ini')
	try:
		if config['SYSTEM']['premature_exit'] == 'yes':
			print("Telling ajax the program was interrupted")
			return json.dumps({'status' : 'OK', 'spider_interrupted' : 1})
	except:
		pass

	lines = []
	try:
		with open('progress.txt', 'r') as f:
			lines = f.read().splitlines()
	except:
		#No data to display
		return json.dumps({'status' : 'OK', 'data' : str(lines), 'new_progress' : 0})

	try:
		if config['PROGRESS']['finished'] == '1':

			try:
				os.remove('progress.txt')
			except:
				print('Failed to remove file \"progress.txt\"')
				pass

			print("Telling Ajax the spider is finished")
			return json.dumps({'status' : 'OK', 'data' : str(lines), 'new_progress' : 1, 'spider_finished' : 1, 'spider_interrupted' : 0})
	except:
		return json.dumps({'status' : 'OK', 'data' : str(lines), 'new_progress' : 1, 'spider_finished' : 0, 'spider_interrupted' : 0})
	return json.dumps({'status' : 'OK', 'data' : str(lines), 'new_progress' : 1, 'spider_finished' : 0, 'spider_interrupted' : 0})

@app.route('/results', methods=['GET'])
def results():
	print("GOING TO RESULTS PAGE")
	data = []
	try:
		with open('full_results.json', 'r') as f:
			data = json.load(f)
			#remove this try/catch to test the results page without running the program again
			
			try:
				os.remove("full_results.json")
			except OSError:
				print('Failed to remove file \"full_results.json\"')
				pass
			
	except Exception as e:
		return render_template('index.html', errormsg="Something went wrong. No spider generated any results. -> " + str(e))
	
	config = configparser.ConfigParser()
	config.read('default_settings.ini')

	try:
		_time = time_string(request.args.get('time'))
		if config['SYSTEM']['runner'] == 'default':
			return render_template('results_fullscan.html', results=data, url=config['DEFAULT']['start_url'], time=_time)

		if config['SYSTEM']['runner'] == 'quick':
			return render_template('results_quickscan.html', results=data, url=config['DEFAULT']['start_url'], time=_time)

		if config['SYSTEM']['runner'] == 'advanced':
			return render_template('results_advanced.html', results=data, url=config['DEFAULT']['start_url'], time=_time)
	except Exception as e:
		return render_template('index.html', errormsg="Failed to load the results template. -> " + str(e))

	return render_template('index.html', errormsg="Failed to load the results template.")
############################


@app.route('/run_default', methods=['POST'])
def run_default():
	url = 'unknown'
	if request.method == 'POST':
		request_string= request.get_data().decode('utf8')

		#Get the config file and set up the sections
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Section setup (fail-safe)
		config['DEFAULT'] = {}
		config['SYSTEM'] = {}
		config['PROGRESS'] = {}
		config['OPTIONAL'] = {}

		#Add potential HTTP AUTH information to config
		config['DEFAULT']['http_user'] = request.form['http-user-ds']
		config['DEFAULT']['http_pass'] = request.form['http-pass-ds']
		
		#Add potential Optional information to config
		if request.form.get('ExtraThorough-ds'):
			config['OPTIONAL']['extra_thorough'] = 'true'
		else:
			config['OPTIONAL']['extra_thorough'] = 'false'
		
		#Save the updated config file
		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)

		#Initiate the runner and get project settings
		try:
			runner = DefaultRunner.DefaultRunner(get_project_settings())
		except Exception as e:
			print("Cant even get settings here - " + str(e))
			return render_template('index.html', errormsg="Failed to load settings.py -> " + str(e))

		#Get the given url
		url = check_http_in_url(request.form['url'])
		
		#Start the runner in a new thread so the UI doesn't lock
		_thread.start_new_thread(runner.run, (url,))

		#Go to the progress page
		return redirect('/yield')

	#This is a fail-safe that should never activate
	#since the only allowed method is POST which would trigger
	#the above return

	#If any partial results exist, load them, else load the start page
	data = []
	try:
		with open('full_results.json', 'r') as f:
			data = json.load(f)
	except:
		return render_template('index.html', errormsg="Something went wrong. No spider generated any results.")

	#Load the results page with partal results
	return render_template('results_fullscan.html', results=data, _url=url)


@app.route('/run_quickscan', methods=['POST'])
def run_quickscan():


	url = 'unknown'
	# But.. this should only ever be POST since the only allowed method is.. POST
	if request.method == 'POST':
		request_string= request.get_data().decode('utf8')

		#Get the config file and set up the sections
		config = configparser.ConfigParser()
		config.read('default_settings.ini')

		#Section setup (fail-safe)
		config['DEFAULT'] = {}
		config['SYSTEM'] = {}
		config['PROGRESS'] = {}
		config['OPTIONAL'] = {}


		config['DEFAULT']['http_user'] = request.form['http-user-qs']
		config['DEFAULT']['http_pass'] = request.form['http-pass-qs']
		with open('default_settings.ini', 'w') as configfile:
			config.write(configfile)

		runner = QuickScanRunner.QuickScanRunner()
		url = check_http_in_url(request.form['url_quickscan'])

		_thread.start_new_thread(runner.run, (url,))

		return redirect('/yield')
		
	data = []
	try:
		with open('full_results.json', 'r') as f:
			data = json.load(f)
			try:
				os.remove("full_results.json")
			except OSError:
				print('Failed to remove file \"full_results.json\"')
				pass
	except:
		return render_template('index.html', errormsg="Something went wrong. No spider generated any results.")

	return render_template('results_quickscan.html', results=data, _url=url)


@app.route('/pp', methods=['GET'])
def pp():
	return render_template('pp.html')
#Called when user leaves the progress page => program must be interrupted
@app.route('/interrupt', methods=['GET'])
def interrupt():
	programInterrupted()
	#This template will never be rendered in the browser but must be here to avoid flask compilation errror
	return json.dumps({'status' : 'OK'})


def time_string(t):
	t = int(t)
	output = ""

	if t > 3600:
		h_tmp = math.floor(t / 3600)
		t = t - h_tmp * 3600
		output += str(h_tmp) + "h "

	if t > 60:
		m_tmp = math.floor(t / 60)
		t = t - m_tmp * 60
		output += str(m_tmp) + "m "

	output += str(t) + "s"

	return output

def programInterrupted():
	print("Program was interrupted prematurely.")

	#RESET EVERYTHING
	config = configparser.ConfigParser()
	config.read('default_settings.ini')

	config['DEFAULT'] = {}
	config['SYSTEM'] = {}
	config['PROGRESS'] = {}
	config['OPTIONAL'] = {}
	config['PROGRESS']['finished'] = '0'
	config['SYSTEM']['premature_exit'] = 'yes'
	with open('default_settings.ini', 'w') as configfile:
		config.write(configfile)

	#REMOVE EVERYTHING
	try:
		os.remove("full_results.json")
	except OSError:
		print('Failed to remove file \"full_results.json\"')
		pass

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
		os.remove("progress.txt")
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

	#CRASH THE REACTOR
	reactor.crash()

app.run()
