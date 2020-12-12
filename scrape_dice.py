from splinter import Browser
from bs4 import BeautifulSoup

executable_path = {'executable_path': 'chromedriver.exe'}
# Headless true for displaying the browser
browser = Browser('chrome', **executable_path, headless=True)

url = "https://www.dice.com/jobs?countryCode=US&radius=30&radiusUnit=mi&page=1&pageSize=20&language=en"
browser.visit(url)