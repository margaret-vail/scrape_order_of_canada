# Import libraries
import requests, re, os, time, sys, traceback
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

dirname = os.path.dirname(__file__)
log_file = os.path.join(dirname, 'logfile_' + datetime.now().strftime("%Y%m%dt%H%M%S") + '.txt')
output_name = "test_" + datetime.now().strftime("%Y%m%dt%H%M%S") + '.csv'

# Create an URL object
all_url = 'https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22'# Create object page
base_url = 'https://www.gg.ca'

# CSV headers
headers = ["id", "name", "location", "honour", "level", "awarded_date", "invested_date", "full_name", "bio", "status", "detail_url"]

# Create a dataframe
mydata = pd.DataFrame(columns = headers)

def get_data(mydata, award_type="members", search_url = all_url, num_pages=2):

    
    i = 1
    while(i <= num_pages):

        if i == 0:
            page = requests.get(search_url).encoding
        else:
            page = requests.get(search_url+'&page='+str(i))

        page.encoding = "utf-8"

        # parser-lxml = Change html to Python friendly format
        # Obtain page's information
        soup = BeautifulSoup(page.text, 'lxml')

        # Obtain information from tag <table>
        table1 = soup.find('table')
        #table1 = soup.table
        

        # Create a for loop to fill mydata
        for j in table1.find_all('tr')[1:]:
            
            # Get information from List html page
            row_data = j.find_all('td')
            
            name = row_data[0]
            if name is not None:
                name = row_data[0].text.strip()
            else:
                name = 'Possible Error'
            
            location = row_data[1]
            if location is not None:
                location = row_data[1].text.strip()
            else:
                location = 'Possible Error'
            
            honour = row_data[2]
            if honour is not None:
                honour = row_data[2].text.strip()
            else:
                honour = 'Possible Error'        

            # Get information from Detail html page
            more_info_url = row_data[0].contents[1].attrs['href']
            # Real URL
            url2 = base_url+more_info_url
            # Test a particular case URL
            #url2 = "https://www.gg.ca/en/honours/recipients/146-14809"
            
            page2 = requests.get(url2)
            soup2 = BeautifulSoup(page2.text, 'lxml')

            # Check how many awards the person has and select the appropriate one
            num_levels = len(soup2.find_all('h3'))

            # There is multiple awards
            # Find Officer Awards
            if(award_type == "officers"):
                # Check if person has more than one award
                if num_levels > 1:
                    for award in soup2.find_all('h3'):
                        if award.text.strip() == 'Officer of the Order of Canada':
                            level = award.text.strip()
                            parent_tag = award
                # There is only one award
                else:
                    parent_tag = soup2.h3
                    if parent_tag is not None:
                        level = parent_tag.text.strip()
                    else:
                        level = "Possible error"

            # Find Companions Awards
            if(award_type == "companions"):
                # Check if person has more than one award
                if num_levels > 1:
                    for award in soup2.find_all('h3'):
                        if award.text.strip() == 'Companion of the Order of Canada':
                            level = award.text.strip()
                            parent_tag = award
                # There is only one award
                else:
                    parent_tag = soup2.h3
                    if parent_tag is not None:
                        level = parent_tag.text.strip()
                    else:
                        level = "Possible error"

            # Find Companions Awards
            if(award_type == "members"):
                # Check if person has more than one award
                if num_levels > 1:
                    for award in soup2.find_all('h3'):
                        if award.text.strip() == 'Member of the Order of Canada':
                            level = award.text.strip()
                            parent_tag = award                            
                # There is only one award
                else:
                    parent_tag = soup2.h3
                    if parent_tag is not None:
                        level = parent_tag.text.strip()
                    else:
                        level = "Possible error"

            awarded_date_element = parent_tag.findNext('li')
            if awarded_date_element.text.strip().find("Awarded on: ") > -1:
                awarded_date = " ".join(awarded_date_element.text.strip().split()).replace("Awarded on: ","")
            else:
                awarded_date = "Possible error"

            invested_date_element = awarded_date_element.findNext('li')
            if invested_date_element.text.strip().find("Invested on: ") > -1:
                invested_date = " ".join(invested_date_element.text.strip().split()).replace("Invested on: ","")
            else:
                invested_date = "Possible error"            

            biography_element = invested_date_element.findNext('p')
            if biography_element is not None:
                biography = biography_element.text.strip()
            else:
                biography = "Possible error"     

            full_name = soup2.find(id="page-title")
            if full_name is not None:
                full_name = soup2.find(id="page-title").text.strip()
            else:
                full_name = 'Possible Error'

            status = soup2.find(text=re.compile('Deceased'))
            if status is None:
                    status = 'Alive'
            else:
                status = soup2.find(text=re.compile('Deceased')).strip()
            
            uid = more_info_url.replace("/en/honours/recipients/","")
            
            detail_url = url2

            row = [uid, name, location, honour, level, awarded_date, invested_date, full_name, biography, status, detail_url]

            length = len(mydata)
            mydata.loc[length] = row

        i = i+1

    return mydata


member_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22149%22"
officer_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22148%22"
companion_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22147%22"

# Real number of pages
total_num_pages_member = 195
total_num_pages_officer = 99
total_num_pages_companion = 20

# Get Members
#mydata = get_data(mydata,"members",member_url,2)
# Get Officers
mydata = get_data(mydata,"officers",officer_url,2)
# Get Companions
mydata = get_data(mydata,"companions",companion_url,2)
    
mydata.to_csv(os.path.join(dirname, output_name), index=False)