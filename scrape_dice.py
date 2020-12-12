import requests
from bs4 import BeautifulSoup as bs
import json
import pymongo
import time
import concurrent.futures
from datetime import date, timedelta
import re

from requests_html import AsyncHTMLSession
from requests_html import HTMLSession
import pyppdf.patch_pyppeteer
import asyncio
import gc

def scrape_job_cards_dice(session, search_string, location, start_page):
    
    #query URL
    url = f"""https://www.dice.com/jobs?{location}&radius=30&radiusUnit=mi&page={start_page}&pageSize=5&filters.employmentType=FULLTIME&language=en"""

    #get asynchronous request from search page
    r = session.get(url)
    
    # perform response rendering (running javascripts)
    print("rendering...")
    r.html.render()
    print("render finished")

search_string = "analyst"
location = "US"
start_page=1

# for start_page in [1,2,3,4,5]:
#     loop = asyncio.get_event_loop()
#     # Scrape and store in DB
#     cards = loop.run_until_complete(scrape_job_cards_dice(asession, search_string, location, start_page))
#     print(start_page)
# loop.close()

for start_page in range(1,20):
    # Scrape and store in DB
    with session = HTMLSession() as conn:
        print(f"Page: {start_page}")
        scrape_job_cards_dice(session, search_string, location, start_page)
        # Garbage collection
    gc.collect()
