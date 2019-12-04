import scrapy
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.http import FormRequest
from scrapy.selector import Selector
from urllib.parse import urlparse
from urllib.parse import urlsplit


from subprocess import check_output

from ..ResultsHandler import ResultsHandler
from ..ProgressHandler import ProgressHandler

import math

from ..InputGenerator import InputGenerator


import sys
import json
import re
import rstr
import configparser
import time
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
#from items import LinkSchemeSpiderItem


class FullSiteSpiders(CrawlSpider):
    name = 'FullSiteSpiders'
    custom_settings = {
        'CLOSESPIDER_PAGECOUNT' : 2000,
        'CLOSESPIDER_TIMEOUT' : 15,
        'RETRY_ENABLED' : False
    }
    handle_httpstatus_list = [404, 500]

    is_running_forms = True
    is_running_cookies = True
    is_running_boxes = True
    is_running_thirdpartyrequests = True

    progress_pre = ""


    def __init__(self, url = None, *args, **kwargs):
        #super(FullSiteSpiders, args[0]).__init__(*args, **kwargs)

        #This config file holds the running choices made in the GUI
        config = configparser.ConfigParser()
        if not config.read('default_settings.ini'):
            raise IOError('cannot load default_settings')

        #Initiate the spider before starting first request
        self.http_user = config['DEFAULT']['http_user']
        self.http_pass = config['DEFAULT']['http_pass']
        self.allowed_domains = [config['DEFAULT']['allowed_domain']]
        self.start_urls = [url]

        #Used to decide what to print as progress (status)
        progress_output = ["Dumping Forms", "Analysing Cookies", "Scanning Checkboxes", "Analysing Third-party requests"]
        joiner = " & "


        #To work with advanced mode, we must be able to run
        #this spider in parts

        if config['SYSTEM']['runner'] == 'advanced' or config['SYSTEM']['runner'] == 'quick':
            if config['SPIDERS']['FormSpider'] == '0':
                progress_output.remove("Dumping Forms")
                self.is_running_forms = False

            if config['SPIDERS']['CookiesSpider'] == '0':
                progress_output.remove("Analysing Cookies")
                self.is_running_cookies = False

            if config['SPIDERS']['ThirdPartyRequestSpider'] == '0':
                progress_output.remove("Analysing Third-party requests")
                self.is_running_thirdpartyrequests = False

            if config['SPIDERS']['BoxCheckSpider'] == '0':
                progress_output.remove("Scanning Checkboxes")
                self.is_running_boxes = False
            else:
                handler = ResultsHandler()
                handler.appendArrayToExistingKey("BoxCheckSpider", "did_run", "smth")

        if config['SYSTEM']['runner'] == 'default':
            if config['OPTIONAL']['extra_thorough'] != 'true':
                progress_output.remove("Dumping Forms")
                self.is_running_forms = False


        phandler = ProgressHandler()
        phandler.append("Analysing " + url)




    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_item)

    def parse_item(self, response):
        config = configparser.ConfigParser()
        config.read('default_settings.ini')
        try:

            #This flag is not used anymore, remove this check C A R E F U L L Y
            if config['PROGRESS']['finished'] == 'interrupted':
                #Program was interrupted
                return
        except Exception as e:
            print('error1 ->', str(e))
            pass



            """
            ***************
            LinkSchemeSpider
            ***************
            """
        if response.request.method == 'GET':
            #Ignore POST requests
            handler = ResultsHandler()
            #Log status code
            handler.appendArrayArrayToExistingKey("StatusSpider", str(response.status), response.request.url)
            #Log n.o pages
            handler.incrementCounterWithKey("Counter")


        #needed?
        if response.status != 200:
            return

        selectius = None
        try:
            selectius = Selector(response)
        except Exception as e:
            print('error2 ->', str(e))
            return


        #all_links = response.xpath('*//a/@href').extract()

        #for link in all_links:
        #    yield response.follow(url=link, callback=self.parse_item)

            """
            ***************
            /LinkSchemeSpider
            ***************
            """


            """
            ***************
            FormSpider
            ***************
            """

        if self.is_running_forms:
            try:
                forms = response.xpath('*//form').extract()
                if forms:
                    for req in self.handleForm(forms):
                        yield req
            except Exception as e:
                print("4 - " + str(e))
            """
            ***************
            /FormSpider
            ***************
            """


        """
        ***************
        BoxCheckSpider
        ***************
        """
            #remove try catch, maybe not...
        if self.is_running_boxes:
            try:
                if not response.xpath('//form//input[contains(@type, "checkbox")]').extract():
                    raise ValueError('No checkbox found on page')

                #print("\n------- BOXER SPIDER ----------")
                prechecked_boxes_found = []

                config = configparser.ConfigParser()
                config.read('default_settings.ini')

                cookies = ""
                #TODODDOD: Maybe not every page will respond with set-cookie == cookies erased
                for cookie in response.headers.getlist('Set-Cookie'):
                    cookies += cookie.decode('utf-8')
                    cookies += "---ENDCOOKIE---"

                content = check_output(['./phantomjs', '--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'page_wait.js', response.url, self.http_user, self.http_pass, cookies, self.allowed_domains[0]])
                
                hxs = Selector(text=content)
                boxes_found = hxs.css("input:checked[type='checkbox']").extract()
                for box in boxes_found:
                    #TODO: This is not enough to say a box is checked
                    #for instance a box with class="not_checked" would
                    #be marked as prechecked
                    #if "checked" in box.lower():
                    phandler = ProgressHandler()
                    phandler.append("Found a prechecked box at: <span class=\"italicized\">" + response.url + "</span>")
                    prechecked_boxes_found.append(box)

                if prechecked_boxes_found:
                    handler = ResultsHandler()
                    handler.appendArrayToExistingKey('BoxCheckSpider', response.url, prechecked_boxes_found)
            except Exception as e:
                #not really an error more like a bad way to skip code
                print('error4 ->', str(e))
                #Borde skapa loggfil
                pass
                
            """
            ***************
            /BoxCheckSpider
            ***************
            """


            #Prepare Cookie and Thirdparty spiders
        try:
            if self.is_running_thirdpartyrequests or self.is_running_cookies:
                output = check_output(['./phantomjs','--ignore-ssl-errors=true', '--ssl-protocol=any','--web-security=false', 'read_cookies_and_resources.js', response.url, config['DEFAULT']['http_user'], config['DEFAULT']['http_pass']])
                all_resources, all_cookies = output.decode().split("---END_RESOURCES---")
        except Exception as e:
            print('could not get cookies/thirdpartyrequests: -> ' + str(e))
            pass
        """
        ***************
        CookieSpider
        ***************
        """
        if self.is_running_cookies:
            try:
                all_cookies = self.striptease(all_cookies)
                with open('all_cookies.json' , 'w') as f:
                    f.write(all_cookies)

                success = False
                while not success:
                    try:
                        with open('all_cookies.json') as data:
                            jsonCookieObject = json.load(data)
                        success = True
                    except Exception as e:
                        line = re.search(r"(?<=line )(.*)(?= column)", str(e))
                        self.removeErrorFromCorruptJson(line.groups()[0], 'all_cookies.json')

                firstpartycookies = {'Cookies': [], 'Grade': 0}
                thirdpartycookies = {'Cookies': [], 'Grade': 0}
                firstpartycookie_grade = 0
                thirdpartycookie_grade = 0
                
                
                with open('full_results.json') as json_data:
                    resultfile = json.load(json_data)
                    #----------------------------------------------------------------------------------------
                    #Kolla ifall det är första gången spindeln körs, kakorna behöver då sparas med appendData.
                    #----------------------------------------------------------------------------------------
                    if not resultfile.get('FirstPartyCookies'):
                        
                        for cookie in jsonCookieObject:
                            #Ifall den aktuella sidans domän inte är den samma som cookien är det en tredjepartscookie:
                            if config['DEFAULT']['allowed_domain'] not in cookie['domain']:
                                thirdpartycookies['Cookies'].append(cookie)
                                phandler = ProgressHandler()
                                phandler.append('Thirdpartycookie found from: ' + cookie['domain'])
                                #Printa ut på loading sidan att en tredjepartscookie har hittats.
                            else:
                                firstpartycookies['Cookies'].append(cookie)
                                phandler = ProgressHandler()
                                phandler.append('Cookie found from: ' + cookie['domain'])
                        #------------------------------------------------------------------------------------
                        #Betygsätta alla firstpartycookies:
                        #------------------------------------------------------------------------------------
                        for cookie2 in firstpartycookies['Cookies']:
                            if cookie2['httponly']:
                                firstpartycookie_grade += 50
                            if cookie2['secure']:
                                firstpartycookie_grade += 50
                        #Lägga till betyget i dict som ska sparas.
                        try:
                            firstpartycookie_grade = math.ceil(firstpartycookie_grade / len(firstpartycookies['Cookies']))
                            firstpartycookies['Grade'] = firstpartycookie_grade
                        except Exception as e:
                            print('firstpartycookies var tom: '+ str(e))

                        #------------------------------------------------------------------------------------
                        #Betygsätta alla tredjepartscookies:
                        #------------------------------------------------------------------------------------
                        for cookie3 in thirdpartycookies['Cookies']:
                            if cookie3['httponly']:
                                thirdpartycookie_grade += 50
                            if cookie3['secure']:
                                thirdpartycookie_grade += 50
                        try:
                            thirdpartycookie_grade = math.ceil(thirdpartycookie_grade / len(thirdpartycookies['Cookies']))
                            thirdpartycookies['Grade'] = thirdpartycookie_grade
                        except Exception as e:
                            print('thirdpartycookies var tom: ' + str(e))
                        #------------------------------------------------------------------------------------
                        handler = ResultsHandler()
                        handler.appendData('FirstPartyCookies', firstpartycookies)
                        handler.appendData('ThirdPartyCookies', thirdpartycookies)
                    #------------------------------------------------------------------------------------
                    #Första körningen är klar.
                    #------------------------------------------------------------------------------------

                    #------------------------------------------------------------------------------------
                    #Ifall det redan finns kakor sparade
                    #------------------------------------------------------------------------------------

                    if resultfile.get('FirstPartyCookies'):

                        existing_thirdpartycookies = {c['name'] for c in resultfile['ThirdPartyCookies']['Cookies']}
                        existing_firstpartycookies = {c['name'] for c in resultfile['FirstPartyCookies']['Cookies']}
                        found_new_thirdpartycookie = False
                        found_new_firstpartycookie = False

                        for cookie in jsonCookieObject:
                            #Kolla ifall tredjepartcookien redan finns!
                            if config['DEFAULT']['allowed_domain'] not in cookie['domain']:
                                if not any(name == cookie['name'] for name in existing_thirdpartycookies):
                                    #den hittade cookien är unik:
                                    thirdpartycookies['Cookies'].append(cookie)
                                    phandler = ProgressHandler()
                                    phandler.append('Thirdpartycookie found from: ' + cookie['domain'])
                                    found_new_thirdpartycookie = True

                            else:
                                #det är en första parts cookie:
                                if not any(name == cookie['name'] for name in existing_firstpartycookies):
                                    #den hittade cookien är unik:
                                    firstpartycookies['Cookies'].append(cookie)
                                    phandler = ProgressHandler()
                                    phandler.append('Cookie found from: ' + cookie['domain'])
                                    found_new_firstpartycookie = True

                        if found_new_thirdpartycookie:
                            for cookie3 in thirdpartycookies['Cookies']:
                                if cookie3['httponly']:
                                    thirdpartycookie_grade += 50
                                if cookie3['secure']:
                                    thirdpartycookie_grade += 50
                            #Räkna ut det nya betyget:
                            lengths = len(thirdpartycookies['Cookies']) + len(resultfile['ThirdPartyCookies']['Cookies'])
                            grades = resultfile['ThirdPartyCookies']['Grade'] * len(resultfile['ThirdPartyCookies']['Cookies'])
                            thirdpartycookie_grade = math.ceil((thirdpartycookie_grade + grades) / lengths)
                            thirdpartycookies['Grade'] = thirdpartycookie_grade

                            try:
                                handler = ResultsHandler()
                                handler.appendCookieToExistingKey('ThirdPartyCookies', thirdpartycookies)
                            except Exception as e:
                                print(str(e))
                        if found_new_firstpartycookie:
                            for cookie2 in firstpartycookies['Cookies']:
                                if cookie2['httponly']:
                                    firstpartycookie_grade += 50
                                if cookie2['secure']:
                                    firstpartycookie_grade += 50
                            #Räkna ut det nya betyget:
                            lengths = len(firstpartycookies['Cookies']) + len(resultfile['FirstPartyCookies']['Cookies'])
                            grades = resultfile['FirstPartyCookies']['Grade'] * len(resultfile['FirstPartyCookies']['Cookies'])

                            firstpartycookie_grade = math.ceil((firstpartycookie_grade + grades) / lengths)
                            firstpartycookies['Grade'] = firstpartycookie_grade

                            handler = ResultsHandler()
                            handler.appendCookieToExistingKey('FirstPartyCookies', firstpartycookies)

                    #------------------------------------------------------------------------------------
                    #Nya kakor är tillagda!
                    #------------------------------------------------------------------------------------
               

            except Exception as e:
                print('Cookiespider error:')
                print("\t" + str(e))

            """
            ***************
            /CookieSpider
            ***************
            """


            """
            ***************
            ThirdPartyRequestSpider
            ***************
            """      
        if self.is_running_thirdpartyrequests:
            existing_thirdpartyrequests = []
            thirdpartyrequests = {"Thirdpartyrequests": [], "https": 0, "http": 0}
            with open('all_resorces_.json', 'w') as f:
                f.write(all_resources)
            try:
                with open('full_results.json') as existing_data:
                    data = json.load(existing_data)
                
                if data.get('ThirdPartyRequestSpider'):
                    thirdpartyrequests = data['ThirdPartyRequestSpider']
                    existing_thirdpartyrequests = [c['Domain'] for c in data['ThirdPartyRequestSpider']['Thirdpartyrequests']]
                    #print('FOUND EXISTING DATA, LIST IS NOW: ' + str(thirdpartyrequests))
                   
            except Exception as e:
                print('No thirdpartyrequests found!')

            success = False
            while not success:
                try:
                    with open('all_resorces_.json') as data:
                        json_resourceData = json.load(data)
                    #print('JSON-file OK!')
                    success = True

                except Exception as e:
                    print('Fixing corrupt JSON-file...')
                    line = re.search(r"(?<=line )(.*)(?= column)", str(e))
                    #print('Error: ' + str(e) + 'LINENUMBER: ' + line.groups()[0])

                    self.removeErrorFromCorruptJson(line.groups()[0], 'all_resorces_.json')
                    
                

            for resource in json_resourceData[:-1]:
                try:
                    url = resource['url']
                    #print(url)
                except Exception as e:
                    print('error2 :  ' + str(e))

                try:
                    if url[:5] == 'https':
                        
                        url_domain = self.getDomainFromUrl(url)
                        if config['DEFAULT']['allowed_domain'] not in url_domain:
                            
                            try:
                                if not any(domain == url_domain for domain in existing_thirdpartyrequests):
                                    phandler = ProgressHandler()
                                    #print(url_domain)
                                    phandler.append('Third-party request found from: ' + url_domain)
                                    domain_2_add = {"Domain": url_domain, "Url": url}
                                    thirdpartyrequests["https"] += 1
                                    thirdpartyrequests["Thirdpartyrequests"].append(domain_2_add)
                                    existing_thirdpartyrequests.append(url_domain)


                            except Exception as e:
                                print('error3-3p-request :' + str(e))

                    elif url[:4] == 'http':
                        url_domain = self.getDomainFromUrl(url)
                        if config['DEFAULT']['allowed_domain'] not in url_domain:
                            
                            try:
                                if not any(domain == url_domain for domain in existing_thirdpartyrequests):
                                    phandler = ProgressHandler()
                                    #print(url_domain)
                                    phandler.append('Third-party request found from: ' + url_domain)
                                    domain_2_add = {"Domain": url_domain, "Url": url}
                                    thirdpartyrequests["http"] += 1
                                    thirdpartyrequests["Thirdpartyrequests"].append(domain_2_add)
                                    existing_thirdpartyrequests.append(url_domain)


                            except Exception as e:
                                print('error3-3p-request :' + str(e))

                                  
                except Exception as e:
                    print('error4-4p-request' + str(e))
            try:
                handler = ResultsHandler()
                #print('lägger till =  '+ str(thirdpartyrequests))
                handler.appendData('ThirdPartyRequestSpider', thirdpartyrequests)
            except Exception as e:
                print('failed to append requests: ' + str(e))


            """
            ***************
            /ThirdPartyRequestSpider
            ***************
            """



    def getDomainFromUrl(self, _url):
        domain =  "{0.netloc}".format(urlsplit(_url))
        if domain[0:4] == 'www.':
            domain = domain[4:]
        return domain



    def removeErrorFromCorruptJson(self, line_number, filename):
        
        number = int(line_number)
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            with open('test.json' , 'w') as f:
                for line in lines:
                    f.write(line)

            with open('test.json') as f, open(filename, 'w') as fo:
                for linenum, line in enumerate(f, start=1):
                    if linenum != number:
                        fo.write(line)

        except Exception as e:
            print('error in func : ' + str(e))
        



            
    def striptease(self, data):
        
        try:
            index = data.find("[")
            return data[index:]
        except Exception as e:
            print(str(e))
            return "[]"
    




    def handleForm(self, forms):
        """
            Called when a form is found on a page.
            forms - all the forms found on the page in plaintext
        """
        try:
        #This is a variable for all the requests that will be
        #made and this variable is returned at the end
            requests_created = []

            #We might have found multiple forms on one page
            #so we need a for loop
            for form in forms:

                #Create a selector that makes it easier
                #to extract the data we need to make a request
                selectius = Selector(text=form)


                #Extract the forms action, so we know where
                #to send the request later
                action = selectius.xpath("*//@action").extract_first()

                #If the url is relative, we must add http
                #TODO: Do we also have to add www in some cases?
                #TODO: Do we need to use https in some cases?
                if 'http' not in action[0:4]:
                    action = 'http://' + self.allowed_domains[0] + action

            #Extract the forms action, so we know where
            #to send the request later
            try:
                action = selectius.xpath("*//@action").extract_first()
            except  Exception as e:
                print("5 - " + str(e))
            #If the url is relative, we must add http
            #TODO: Do we also have to add www in some cases?
            #TODO: Do we need to use https in some cases?
            if 'http' not in action[0:4]:
                action = 'http://' + self.allowed_domains[0] + action


                #Extract all names, WHY THOUGH??????
                names = selectius.xpath("*//@name").extract()

                #Empty template for the final request data
                formulated_request = {}


                #Iterate through all the input lines
                for inputField in selectius.xpath("*//input").extract():
                    inputSelector = Selector(text=inputField)


                    #If name is not found for a field, it would
                    #create a "null" key in the request which
                    #would fail
                    name = inputSelector.xpath("*//@name").extract_first()
                    if not name:
                        continue

            #Iterate through all the input lines
            for inputField in selectius.xpath("*//input").extract():
                inputSelector = Selector(text=inputField)
                """
                try:
                    pattern = inputSelector.xpath("*//@pattern").extract_first()
                    print("pattern: " + pattern)
                    val = rstr.rstr(pattern)
                    print(val)
                    return val
                except Exception as e:
                    print("6 - " + str(e))
                    pass
                """
                #If name is not found for a field, it would
                #create a "null" key in the request which
                #would fail
                name = inputSelector.xpath("*//@name").extract_first()
                if not name:
                    continue

                #Extract field prefilled value (if exists)
                value = inputSelector.xpath("*//@value").extract_first()

                #If the value is empty or None,
                #Meaning there is no prefilled data in
                #that field, we try to guess what fits there
                #if the guess fails (which should be impossible, btw)
                #we just put random data, literally
                if value == "" or not value or value == "randomdata": 
                    try:
                        #Try to guess input, if this fails it's probably because xpath failed to find type
                        formulated_request[name] = self.guessInput(inputSelector, name)
                    except:
                        formulated_request[name] = "randomdata"
                else:
                    #in case its a number or smth, we must convert to string
                    formulated_request[name] = str(value)


                    #Extract field prefilled value (if exists)
                    value = inputSelector.xpath("*//@value").extract_first()

                    #If the value is empty or None,
                    #Meaning there is no prefilled data in
                    #that field, we try to guess what fits there
                    #if the guess fails (which should be impossible, btw)
                    #we just put random data, literally
                    if value == "" or not value or value == "randomdata": 
                        try:
                            #Try to guess input, if this fails it's probably because xpath failed to find type
                            formulated_request[name] = self.guessInput(inputSelector, name)
                        except:
                            formulated_request[name] = "randomdata"
                    else:
                        #in case its a number or smth, we must convert to string
                        formulated_request[name] = str(value)


                #This is a safeguard against null values,
                #should not be needed but nice to have
                formulated_request.pop('null', None)
                formulated_request.pop("null", None)

                try:
                    with open("forms_sent.txt", "r") as f:
                        lines = [x.strip('\n') for x in f.readlines()]
                        if action + json.dumps(formulated_request) in lines:
                            continue
                except:
                    pass

                #Create a FormRequest and add it to the return list
                try:
                    with open("forms_sent.txt", "a") as f:
                        appiend = action + json.dumps(formulated_request)
                        f.write(appiend + "\n")

                    phandler = ProgressHandler()
                    phandler.append("Form post request sent")

                    requests_created.append(FormRequest(url=action, method='POST', callback=self.parse_item, formdata=formulated_request))

                except Exception as e:
                    print("Request failed - " + str(e))

            return requests_created
        except Exception as e:
            print('handling forms error ->' + str(e))
            pass

    def guessInput(self, selector, name):
        #Try to guess what input fits best for a field
        #We need the whole selector in case we also need to
        #get attributes like maxlength
        #also name can be used to guess things like email inputs

        #TODO: Would be nice to match regex (input pattern=regex)

        #Bake everything in try/catch because, just because
        try:
            #Extract the input type
            inputType = selector.xpath("*//@type").extract_first()

            #input type=button
            #input type=checkbox
            #input type=file
            #input type=hidden
            #input type=image

            #input type=password
            #(trying to match every imaginable password requirement [except whitespace])
            if inputType.lower() == 'password':
                return "9BsH23_!&-jgUQ"

            #Try to handle checkbox without default value
            elif inputType.lower() == 'checkbox':
                return "on"    

            #input type=textarea
            elif inputType.lower() == 'textarea':
                return "Lorem Ipsum Dolor Sit Amet"

            #input type=text #ADD INPUT TYPE HIDDEN
            else:
                #TODO:
                #Theese "guessers" need to be ordered by priority
                #ex. should name=password_email trigger password or email guesser

                #email guesser
                if re.match('\w*(e[-]*[_]*post)\w*', name, re.IGNORECASE) or re.match('\w*(mail)\w*', name, re.IGNORECASE) or re.match('\w*(e-post)\w*', name, re.IGNORECASE):
                    mail = ""
                    try:
                        with open("mail.txt", "r") as f:
                            mail = f.read()
                        #somewhere along the way something happened that
                        #overwrote the mail, so...
                        if mail == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        mail = iptgen.generate_email()
                        with open("mail.txt", "w") as f:
                            f.write(mail)

                    return mail

                #username guesser
                if re.match('\w*(anv[-]*[_]*namn)\w*', name, re.IGNORECASE) or re.match('\w*(user[-]*[_]*name)\w*', name, re.IGNORECASE):
                    #Use the same username
                    username = ""
                    try:
                        with open("username.txt", "r") as f:
                            username = f.read()
                        #somewhere along the way something happened that
                        #overwrote the username, so...
                        if username == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        username = iptgen.generate_username()
                        with open("username.txt", "w") as f:
                            f.write(username)

                    return username


                #firstname guesser
                if re.match('\w*(for[-]*[_]*namn)\w*', name, re.IGNORECASE) or re.match('\w*(first[-]*[_]*name)\w*', name, re.IGNORECASE):
                    firstname = ""
                    try:
                        with open("firstname.txt", "r") as f:
                            firstname = f.read()
                        #somewhere along the way something happened that
                        #overwrote the firstname, so...
                        if firstname == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        firstname = iptgen.generate_firstname()
                        with open("firstname.txt", "w") as f:
                            f.write(firstname)

                    return firstname

                #lastname guesser
                if re.match('\w*(efter[-]*[_]*namn)\w*', name, re.IGNORECASE) or re.match('\w*(last[-]*[_]*name)\w*', name, re.IGNORECASE):
                    lastname = ""
                    try:
                        with open("lastname.txt", "r") as f:
                            lastname = f.read()
                        #somewhere along the way something happened that
                        #overwrote the lastname, so...
                        if lastname == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        lastname = iptgen.generate_lastname()
                        with open("lastname.txt", "w") as f:
                            f.write(lastname)

                    return lastname

                #address guesser
                if re.match('\w*(address)\w*', name, re.IGNORECASE) or re.match('\w*(adress)\w*', name, re.IGNORECASE):
                    address = ""
                    try:
                        with open("address.txt", "r") as f:
                            address = f.read()
                        #somewhere along the way something happened that
                        #overwrote the address, so...
                        if address == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        address = iptgen.generate_address()
                        with open("address.txt", "w") as f:
                            f.write(address)

                    return address

                #phonenumber guesser
                if re.match('\w*(phone)\w*', name, re.IGNORECASE) or re.match('\w*(tel)\w*', name, re.IGNORECASE) or re.match('\w*(mobil)\w*', name, re.IGNORECASE):
                    phone = ""
                    try:
                        with open("phone.txt", "r") as f:
                            phone = f.read()
                        #somewhere along the way something happened that
                        #overwrote the phone, so...
                        if phone == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        phone = iptgen.generate_phonenumber()
                        with open("phone.txt", "w") as f:
                            f.write(phone)

                    return phone

                #country guesser 
                if re.match('\w*(land)\w*', name, re.IGNORECASE):
                    country = ""
                    try:
                        with open("country.txt", "r") as f:
                            country = f.read()
                        #somewhere along the way something happened that
                        #overwrote the country, so...
                        if country == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        country = "Sverige"
                        with open("country.txt", "w") as f:
                            f.write(country)

                    return country
                #country guesser 
                if re.match('\w*(country)\w*', name, re.IGNORECASE):
                    country = ""
                    try:
                        with open("country.txt", "r") as f:
                            country = f.read()
                        #somewhere along the way something happened that
                        #overwrote the country, so...
                        if country == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        country = "Sweden"
                        with open("country.txt", "w") as f:
                            f.write(country)

                    return country

                #Zipcode guesser
                if re.match('\w*(zip)\w*', name, re.IGNORECASE) or re.match('\w*(post[-]*[_]*nr)\w*', name, re.IGNORECASE) or re.match('\w*(post[-]*[_]*nummer)\w*', name, re.IGNORECASE):
                    zipcode = ""
                    try:
                        with open("zipcode.txt", "r") as f:
                            zipcode = f.read()
                        #somewhere along the way something happened that
                        #overwrote the zipcode, so...
                        if zipcode == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        zipcode = "11121"
                        with open("zipcode.txt", "w") as f:
                            f.write(zipcode)

                    return zipcode

                #City guesser
                if  re.match('\w*(ort)\w*', name, re.IGNORECASE)  or re.match('\w*(stad)\w*', name, re.IGNORECASE) or re.match('\w*(city)\w*', name, re.IGNORECASE):
                    city = ""
                    try:
                        with open("city.txt", "r") as f:
                            city = f.read()
                        #somewhere along the way something happened that
                        #overwrote the city, so...
                        if city == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        city = "Stockholm"
                        with open("city.txt", "w") as f:
                            f.write(city)

                    return city


                #Social security number guesser
                if  re.search('\w*(p[-]*[_]*nr)\w*', name, re.IGNORECASE)  or re.match('\w*(person[-]*[_]*nummer)\w*', name, re.IGNORECASE) or re.match('\w*(person[-]*[_]*nr)\w*', name, re.IGNORECASE) or re.match('\w*(social)\w*', name, re.IGNORECASE):
                    social = ""
                    try:
                        with open("social.txt", "r") as f:
                            social = f.read()
                        #somewhere along the way something happened that
                        #overwrote the social, so...
                        if social == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        #phone number is 10 numbers, good enough
                        social = iptgen.generate_social()
                        with open("social.txt", "w") as f:
                            f.write(social)

                    return social

                #Company guesser
                if  re.match('\w*(foretag)\w*', name, re.IGNORECASE)  or re.match('\w*(company)\w*', name, re.IGNORECASE):
                    company = ""
                    try:
                        with open("company.txt", "r") as f:
                            company = f.read()
                        #somewhere along the way something happened that
                        #overwrote the city, so...
                        if company == "randomdata":
                            raise ValueError('Didn\'t expect to find randomdata here...')
                    except:
                        iptgen = InputGenerator()
                        company = iptgen.generate_company()

                        with open("company.txt", "w") as f:
                            f.write(company)

                    return company


                #TODO:
                #ALOT more guessers could be made
                #like - state, etc...
                #Do we need to check for password in text field even though it should never exist?


        except Exception as e:
            #couldn't guess, probably because
            #no type was found, i.e selector failed,
            #so just return randomdata, literally
            print("Returning randomdata because of error - " + str(e))
            return "randomdata"

        #How can this be reached?
        return "randomdata"


    def closed(self, reason):
        #TODO: (maybe do in runner instead)
        #Clean up stuff here
        #namely:
        # username.txt, mail.txt, firstname.txt, lastname.txt, address.txt, phone.txt, forms_sent.txt, forms.txt
        print("Closing - " + reason)



