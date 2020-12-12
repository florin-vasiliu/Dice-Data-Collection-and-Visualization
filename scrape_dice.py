import pymongo
from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import time

executable_path = {'executable_path': 'chromedriver.exe'}
# Headless False for displaying the browser
browser = Browser('chrome', **executable_path, headless=False)

def scrape_job_cards_dice(browser):
    # get html page
    html = browser.html

    #parse request to BeautifulSoup object
    soup = bs(html, 'html.parser')

    #get page job cards
    return soup.find_all('div', class_="card")

def scrape_job_dice(job_card):
    #initiate fields
    job_title = ""
    job_company = ""
    job_salary = ""
    job_location = ""
    job_date = ""
    job_description = ""

    job_title = job_card.find_all(class_="card-title-link")[0].text
    job_company = job_card.find_all(class_="card-company")[0].a.text

    # get location
    job_location = job_card.find_all(id="searchResultLocation")[0].text

    # get full job descr html
    job_descr_link = job_card.find_all(class_="card-title-link")[0].get('href')
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
    job_description = soup.find_all(id="jobdescSec")[0].get_text()

    # job date
    job_date = job_card.find_all(class_="posted-date")[0].text

    #print all found details

    print(f"""
        job_title: {job_title},
        job_company: {job_company},
        job_salary: {job_salary},
        job_location: {job_location},
        job_date: {job_date},
        job_type: {job_type},
        job_description: {job_description[:30]}""")

    return [job_title, job_company, job_salary, job_location, job_date, job_type, job_description]

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

    def store_job(self, title, company, salary, location, date, job_type, description):
        self.jobs_collection.insert_one({ \
        "job_title": title, \
        "job_company": company, \
        "job_salary": salary, \
        "job_location": location, \
        "job_date": date, \
        "job_type": job_type, \
        "job_description": description \
        })

# filtering only fultime jobs
url = "https://www.dice.com/jobs?location=USA&latitude=37.09024&longitude=-95.712891&countryCode=US&locationPrecision=Country&radius=30&radiusUnit=mi&page=1&pageSize=1000&filters.employmentType=FULLTIME&language=en"
browser.visit(url)  

#Initiate database session
session = db_connection()

page = 1

counter = 0
time_start = time.time()
while page <= 35:
    time.sleep(2*60)
    # Scrape and store in DB
    cards = scrape_job_cards_dice(browser)
    for card in cards:
        session.store_job(*scrape_job_dice(card))

        counter+=1
        time_elapsed = time.time() - time_start
        print(f"Page: {page}")
        print(f"Jobs Scraped: {counter}")
        print(f"Time Elapsed[min]: {time_elapsed/60}")
        time.sleep(1)
    
    # Navigate to next page
    browser.click_link_by_partial_text('»')
    page+=1