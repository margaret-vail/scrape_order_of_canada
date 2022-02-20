# Import libraries
import requests, re, os, time, sys, traceback
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

dirname = os.path.dirname(__file__)
log_file_path = os.path.join(dirname, 'logfile_' + datetime.now().strftime("%Y%m%dt%H%M%S") + '.txt')

log_file = open(log_file_path, "w")
log_file.close()

output_name = "order_of_canada_" + datetime.now().strftime("%Y%m%dt%H%M%S") + '.csv'

# Create an URL object
all_url = 'https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22'# Create object page
base_url = 'https://www.gg.ca'

# CSV headers
headers = ["id", "name", "location", "honour", "award_level", "awarded_date", "invested_date", "full_name", "bio", "status", "detail_url"]

# Create a dataframe
mydata = pd.DataFrame(columns = headers)

def get_data(mydata, award_type="members", search_url=all_url, start_page=0, end_page=2):

    
    i = start_page
    while(i < end_page):

        if i == 0:
            page = requests.get(search_url)
        else:
            page = requests.get(search_url+'&page='+str(i))

        page.encoding = "utf-8"

        # parser-lxml = Change html to Python friendly format
        # Obtain page's information
        soup = BeautifulSoup(page.text, 'lxml')

        # Obtain information from tag <table>
        table1 = soup.find('table')
        #table1 = soup.table
        
        try:
            table_loop = table1.find_all('tr')[1:]
        except:
            log_file = open(log_file_path, "a")
            log_file.write( "Table Loop failed: i="+str(i)+ "\n")
            log_file.close()

        # Create a for loop to fill mydata
        for j in table_loop:

            # blank the valuesppython
            uid = ""
            name = ""
            location = ""
            honour = ""
            award_level = ""
            awarded_date = ""
            invested_date = ""
            full_name = ""
            biography = ""
            status = ""
            detail_url = ""

            # Get information from List html page
            row_data = j.find_all('td')
            
            name = row_data[0]
            if name is not None:
                name = row_data[0].get_text().strip()
            else:
                name = 'Possible Error'

            if name == "Georges-Henri Denys Arcand":
                name = "Georges-Henri Denys Arcand"
            
            location = row_data[1]
            if location is not None:
                location = row_data[1].get_text().strip()
            else:
                location = 'Possible Error'
            
            honour = row_data[2]
            if honour is not None:
                honour = row_data[2].get_text().strip()
            else:
                honour = 'Possible Error'        

            # Get information from Detail html page
            more_info_url = row_data[0].contents[1].attrs['href']
            # Real URL
            url2 = base_url+more_info_url
            # Test a particular case URL
            #url2 = "https://www.gg.ca/en/honours/recipients/146-5105"
            #url2 = "https://www.gg.ca/en/honours/recipients/146-96"
            
            page2 = requests.get(url2)
            soup2 = BeautifulSoup(page2.text, 'lxml')

            # Check how many awards the person has and select the appropriate one
            award_groups = soup2.find("div", class_="view-grouping-content").ul
            li = award_groups.find_all("li", recursive=False)
            num_awards = len(li)

            for item in li:
                if award_type == "members":
                    if item.h3.get_text().strip().find('Member of the Order of Canada') > -1:
                        award_level = item.h3.get_text().strip()                            
                    else:
                        continue

                if award_type == "officers":
                    if item.h3.get_text().strip().find('Officer of the Order of Canada') > -1:
                        award_level = item.h3.get_text().strip()                            
                    else:
                        continue

                if award_type == "companions":
                    if item.h3.get_text().strip().find('Companion of the Order of Canada') > -1:
                        award_level = item.h3.get_text().strip()                            
                    else:
                        continue                    
                
                dates = item.find_all("li")
                for date in dates:
                    if date.get_text().strip().find("Awarded on: ") > -1:
                        awarded_date = " ".join(date.get_text().strip().split()).replace("Awarded on: ","")
                    if date.get_text().strip().find("Invested on: ") > -1:
                        invested_date = " ".join(date.get_text().strip().split()).replace("Invested on: ","")
            
                biography_element = item.p
                if biography_element is not None:
                    biography = biography_element.get_text().strip()
                else:
                    biography = ""    

            # Check if there is no invested date
            try:
                if invested_date is None:
                    invested_date = ""
            except:
                invested_date = ""

            # Check if there is no biography
            try:
                if biography is None:
                    biography = ""
            except:
                biography = ""



            full_name = soup2.find(id="page-title")
            if full_name is not None:
                full_name = soup2.find(id="page-title").get_text().strip()
            else:
                full_name = 'Possible Error'

            status = soup2.find(text=re.compile('Deceased'))
            if status is None:
                    status = 'Alive'
            else:
                status = soup2.find(text=re.compile('Deceased')).strip()
            
            uid = more_info_url.replace("/en/honours/recipients/","")
            
            detail_url = url2

            row = [uid, name, location, honour, award_level, awarded_date, invested_date, full_name, biography, status, detail_url]

            length = len(mydata)
            mydata.loc[length] = row


        i = i+1

    return mydata


member_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22149%22"
officer_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22148%22"
companion_url = "https://www.gg.ca/en/honours/recipients?f%5B0%5D=honour_type_id%3A%22146%22&f%5B1%5D=honour_level_id%3A%22147%22"

# Real number of pages
total_num_pages_member = 199
total_num_pages_officer = 101
total_num_pages_companion = 21

# Total Members = 4973
# Total Officers = 2523
# Total Companions = 517

# Get Members
#mydata = get_data(mydata,"members",member_url,0,total_num_pages_member)
# Get Officers
#mydata = get_data(mydata,"officers",officer_url,0,total_num_pages_officer)
# Get Companions
mydata = get_data(mydata,"companions",companion_url,19,total_num_pages_companion)

# Get Members
#mydata = get_data(mydata,"members",member_url,2)
# Get Officers
#mydata = get_data(mydata,"officers",officer_url,2)
# Get Companions
#mydata = get_data(mydata,"companions",companion_url,2)
    
mydata.to_csv(os.path.join(dirname, output_name), index=False)