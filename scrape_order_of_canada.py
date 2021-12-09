# Import libraries
import requests, re, os, time, sys, traceback
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

dirname = os.path.dirname(__file__)
log_file = os.path.join(dirname, 'logfile_' + datetime.now().strftime("%Y%m%dt%H%M%S") + '.txt')

# Create an URL object
url = 'https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22'# Create object page
base_url = 'https://www.gg.ca'

member_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22149%22"
officer_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22148%22"
companion_url = ""

# Test number of pages
total_num_pages_member = 2
total_num_pages_officer = 2
total_num_pages_companion = 2

# Real number of pages
#total_num_pages_member = 195
#total_num_pages_officer = 99
#total_num_pages_companion = 20

# CSV headers
headers = ["id", "name", "location", "honour", "level", "awarded_date", "invested_date", "full_name", "bio", "status", "detail_url"]

# Create a dataframe
mydata = pd.DataFrame(columns = headers)

def sameForEveryone(i):


i = 1

# Get Members
while(i <= total_num_pages_member):

    if i == 0:
        page = requests.get(url)
    else:
        page = requests.get(url+'&page='+str(i))

    # parser-lxml = Change html to Python friendly format
    # Obtain page's information
    soup = BeautifulSoup(page.text, 'lxml')

    # Obtain information from tag <table>
    table1 = soup.find('table')

    # Create a for loop to fill mydata
    for j in table1.find_all('tr')[1:]:
        
        # Get information from List html page
        row_data = j.find_all('td')
        
        try:
            name = row_data[0].text.strip()
        except:
            name = 'Possible Error'
        try:
            location = row_data[1].text.strip()
        except:
            location = 'Possible Error'
        try:
            honour = row_data[2].text.strip()
        except:
            honour = 'Possible Error'        

        # Get information from Detail html page
        more_info_url = row_data[0].contents[1].attrs['href']
        # Real URL
        #url2 = base_url+more_info_url
        # Test a particular case URL
        url2 = "https://www.gg.ca/en/honours/recipients/146-60"
        
        page2 = requests.get(url2)
        soup2 = BeautifulSoup(page2.text, 'lxml')

        try:
            level = soup2.h3.text.strip()
        except:
            level = 'Possible Error'
        try:
            awarded_date = " ".join(soup2.find(text=re.compile('Awarded on')).strip().split()).replace("Awarded on: ","")
        except:
            awarded_date = 'Possible Error'
        try:
            invested_date = " ".join(soup2.find(text=re.compile('Invested on')).strip().split()).replace("Invested on: ","")
        except:
            invested_date = 'Possible Error'
        try:
            full_name = soup2.find(id="page-title").text.strip()
        except:
            full_name = 'Possible Error'
        try:
            bio = soup2.p.text.strip()
        except:
            bio = 'Possible Error'
        try:
            status = soup2.find(text=re.compile('Deceased'))
            if status is None:
                status = 'Alive'
            else:
                status = soup2.find(text=re.compile('Deceased')).strip()
        except:
            status = 'Possible Error'
        
        uid = more_info_url.replace("/en/honours/recipients/","")
        
        detail_url = url2

        row = [uid, name, location, honour, level, awarded_date, invested_date, full_name, bio, status, detail_url]

        i = i+1

    length = len(mydata)
    mydata.loc[length] = row
    
mydata.to_csv(os.path.join(dirname, 'test.csv'), index=False)