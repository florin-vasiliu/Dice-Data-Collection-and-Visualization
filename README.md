# Dice Scraping

## Problem description and Objective
From the perspective of a job seeker willing to relocate in order to find the perfect job, it is very time consuming to navigate through a website by querying keywords for different locations and reading through the job desctiptions individually.
Therefore, this project was developed having this in mind, with the objective to collect job data using keywords, sort these jobs according to the number of matched keywords, and plot them on a map.

## Project development

### 1. Data Scraping:

* Job cards are being scraped using keywords.

 <img src=https://github.com/florin-vasiliu/dice_scraping/blob/master/images/JobCards.JPG>|
 ---|
 Fig.1: Keyword insertion field and example of card data
 
* In order to prevent requesting unnecessarily duplicate job descriptions, the database is queried first with the card data attributes. If data attributes ("JobTitle", "JobCompany", "JobLocation" and "JobDate") are found in the database, job description request is being skiped.
 
  <img src=https://github.com/florin-vasiliu/dice_scraping/blob/master/images/DatabaseSchema.JPG> |
  ---|
  Fig.2: Example of one database entry and atributes queried
  
* Job description is being scraped and text is being prepared and scanned for keywords.

  <img src=https://github.com/florin-vasiliu/dice_scraping/blob/master/images/JobDescription.JPG> |
  ---|
  Fig.3: Job description example
  
* Job coordinates are being added using the location from the card data.
  
* Collected and processed data is stored in the database (fig.2)
  
 ### 2. Data Visualization:
 
* Data is being displayed in the form of a heatmap and a list. The list displays job data sorted by the percentage of keywords matched. 
  <img src=https://github.com/florin-vasiliu/dice_scraping/blob/master/images/TableauDashboard.JPG> |
  ---|
  Fig.3: Job description example
  
* Data can be filtered by location by dragging and dropping the cursor on the desired area
  <img src=https://media.giphy.com/media/F8L4UlK9Ej40IH6Qag/giphy.gif> |
  ---|
  Fig.4: Filtering by dragging and dropping

* Job description can be accessed by clicking on the "Job_Description_Link" column of the list.

#### A static example of how the Tableau file works can be accessed at the following <a href="https://public.tableau.com/profile/florin.vasiliu4232#!/vizhome/DiceData_16199065191880/JobsDistribution">link</a>
  
  
 
 

