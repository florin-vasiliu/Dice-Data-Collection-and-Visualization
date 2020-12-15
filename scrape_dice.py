import pymongo
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import time
from datetime import date, timedelta
from geopy.geocoders import Nominatim
import re

# count keywords in description
from collections import Counter
def find_words(key_words, string):
    string = string.split()
    separator = " "
    words_found = {}
    for word in key_words:
        n_gram = len(word.split())
        res = Counter(separator.join(string[idx : idx + n_gram]) for idx in range(len(string) - n_gram + 1))
        print(word, res[word])
        if res[word]>0:
            words_found[word] = res[word]
    # add KeyWordsMatch[%]
    words_found["KeyWordsMatch[%]"] = len(words_found)/len(key_words)
    return words_found


# find coordinates for a given address
def find_coordinates(address):     
    # Try with address as is
    geolocator = Nominatim(user_agent="DreamTeam")
    location = geolocator.geocode(address)
    if location is None:
        return {"location_latitude":"", "location_longitude":""}
    else:
        return {"location_latitude":location.latitude, "location_longitude":location.longitude}


# date conversion
def convert_date(date_string):
        if date_string.find("hours ago")>-1:
            return date.today()
        elif date_string.find("hour ago")>-1:
            return date.today()
        elif date_string.find("minutes ago")>-1:
            return date.today()
        elif date_string.find("minute ago")>-1:
            return date.today()
        elif date_string.find("days ago")>-1:
            days_to_substract = re.compile(r'\d+')
            days_to_substract = days_to_substract.findall(date_string)[0]
            return date.today()-timedelta(days=int(days_to_substract))
        elif date_string.find("day ago")>-1:
            return date.today()-timedelta(days=1)

class scrape:
    def __init__(self):
        executable_path = {'executable_path': 'chromedriver.exe'}
        # Headless False for displaying the browser
        self.browser = Browser('chrome', **executable_path, headless=False)
    
    def visit_page(self, location="USA", page_size=100, employment_type = "FULLTIME"):
        # filtering only fultime jobs
        url = f"https://www.dice.com/jobs?location={location}&latitude=37.09024&longitude=-95.712891&countryCode=US&locationPrecision=Country&radius=30&radiusUnit=mi&page=1&pageSize={page_size}&filters.employmentType={employment_type}&language=en"
        self.browser.visit(url) 
        
    def scrape_job_cards_dice(self):
        # get html page
        html = self.browser.html

        #parse request to BeautifulSoup object
        soup = bs(html, 'html.parser')

        #get page job cards and create generator for each card
        cards = soup.find_all('div', class_="card")
        for card in cards:
            #initiate fields
            job_title = ""
            job_company = ""
            job_location = ""
            job_date = ""
            job_descr_link = ""
            
            #get fields from card
            job_title = card.find_all(class_="card-title-link")[0].text
            job_company = card.find_all(class_="card-company")[0].a.text
            job_location = card.find_all(id="searchResultLocation")[0].text
            job_date = card.find_all(class_="posted-date")[0].text
            job_date = str(convert_date(job_date))
            job_descr_link = card.find_all(class_="card-title-link")[0].get('href')
            
            #yield the results
            yield {"job_title":job_title, "job_company":job_company, \
                   "job_location":job_location, "job_date":job_date, "job_descr_link":job_descr_link}
            
    def scrape_job_dice(self, job_descr_link):

        job_descr_html = requests.get(job_descr_link)
        soup = bs(job_descr_html.text, 'html.parser') 

        #check if salary is present or not
        try: 
            job_salary = soup.find_all(class_="mL20")[0].text
        except: 
            job_salary = ''
            
        #check if job type is present or not
        try: 
            job_type = soup.find_all("input",{"id":"empTypeSSDL"})[0]["value"]
        except: 
            job_type = ''

        # job description
        try:
            job_description = soup.find_all(id="jobdescSec")[0].get_text()
        except:
            job_description = ''

        return {"job_salary":job_salary, "job_type":job_type, "job_description":job_description}

# Store in db
class db_connection:
    def __init__(self):
        #connect to database
        connection_string='mongodb://localhost:27017'
        client = pymongo.MongoClient(connection_string)
        #define database for storage
        db = client.dice_db
        #drop all stored data
        #db.jobs.drop()
        db.jobs
        #define collection to store data
        self.jobs_collection = db.jobs
        
    def check_job_presence(self, job_title, job_company, job_location, job_date):
        # check if record is in database before scraping description
        field_to_check = self.jobs_collection.find_one({"$and":[
            {"job_title":job_title},
            {"job_company": job_company},
            {"job_location": job_location},
            {"job_date":job_date}
                                                 ]})
        if field_to_check is not None:
                # print("Job already found in database")
                return True
        else:
            return False
            
    def store_job(self, title, company, location, latitude, longitude, date, salary, job_type, description, words_found_dict):
        self.jobs_collection.insert_one({ \
        "job_title": title, \
        "job_company": company, \
        "job_salary": salary, \
        "job_location": location, \
        "location_latitude": latitude, \
        "location_longitude": longitude, \
        "job_date": date, \
        "job_type": job_type, \
        "job_description": description, \
        **words_found_dict \
        })
        
        print(f"""Inserted into database:
            job_title: {title}
            job_company: {company}
            job_salary: {salary}
            job_location: {location}
            location_latitude: {latitude}
            location_longitude: {longitude}
            job_date: {date}
            job_type: {job_type}
            job_description: {description[:30]}
            words_found: {words_found_dict}
            
            """)

# Define keywords to scrape
key_words = ["data analyst", "data scientist", "excel", "python", "pandas", "matplotlib", "sql", "postgresql", "bootstrap", "nosql", \
    "mongodb", "mongo", "javascript", "tableau", "machine learning", "ml", "scikit learn", "scikit", "keras", "tensorflow", "pyspark", "natural language processing", \
        "nlp", "big data", "etl", "extract transform load", "amazon web services", "aws", "rds"]

# Initiate database session and browser
session = db_connection()
browser = scrape()

# Visit first page
time_to_sleep_for_page_change = 10
time_to_sleep_for_scraping_job_descr = 1
browser.visit_page(page_size=1000)
time.sleep(time_to_sleep_for_page_change)

# Start looping
page = 1

job_inserted_counter = 0
time_start = time.time()
while page <= 350:
    # Scrape and store in DB
    for card_data in browser.scrape_job_cards_dice():
        # if card data is in database then scrape job description and store data
        if not session.check_job_presence( \
            card_data["job_title"], \
            card_data["job_company"], \
            card_data["job_location"], \
            card_data["job_date"], \
                                        ):
            # scrape job description and wait
            job_descr_dict = browser.scrape_job_dice(card_data["job_descr_link"])
            coordinates = find_coordinates(card_data["job_location"])
            time.sleep(time_to_sleep_for_scraping_job_descr)
            
            # store data
            session.store_job(
                card_data["job_title"], \
                card_data["job_company"], \
                card_data["job_location"], \
                coordinates["location_latitude"], \
                coordinates["location_longitude"], \
                card_data["job_date"], \
                job_descr_dict["job_salary"], \
                job_descr_dict["job_type"], \
                job_descr_dict["job_description"], \
                
                #inserting dict of words found in description
                find_words(key_words, job_descr_dict["job_description"])
            )
            job_inserted_counter+=1
            
            time_elapsed = time.time() - time_start
            print(f"Page: {page}")
            print(f"New Jobs Scraped: {job_inserted_counter}")
            print(f"Time Elapsed[min]: {time_elapsed/60}")
    time_elapsed = time.time() - time_start
    print(f"Page: {page}")
    print(f"New Jobs Scraped: {job_inserted_counter}")
    print(f"Time Elapsed[min]: {time_elapsed/60}")
    
    # Navigate to next page
    browser.browser.click_link_by_partial_text('»')
    time.sleep(time_to_sleep_for_page_change)
    page+=1