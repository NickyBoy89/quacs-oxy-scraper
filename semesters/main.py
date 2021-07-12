import requests, json, re, time, sys
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import path
import urllib3

# Ignore the SSL errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

caching = False

dump = {} # Stores the final JSON generated

session = requests.Session() # Initialize the browser session

# Load the homepage and get its data into a session
initialLoad = session.get('https://counts.oxy.edu/public/default.aspx', verify=False)
soup = BeautifulSoup(initialLoad.text, 'html.parser')

data = {
    'ScriptManager2': """pageUpdatePanel|tabContainer$TabPanel1$btnGo""",
    'tabContainer_ClientState': soup.find(id='tabContainer_ClientState')['value'],
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__LASTFOCUS': '',
    '__VIEWSTATE': soup.find(id='__VIEWSTATE')['value'],
    '__VIEWSTATEGENERATOR': soup.find(id='__VIEWSTATEGENERATOR')['value'],
    '__VIEWSTATEENCRYPTED': soup.find(id='__VIEWSTATEENCRYPTED')['value'],
    '__EVENTVALIDATION': soup.find(id='__EVENTVALIDATION')['value'],
    'tabContainer$TabPanel1$ddlSemesters': '202102',
    'tabContainer$TabPanel1$ddlSubjects': '',
    'tabContainer$TabPanel1$txtCrseNum': '',
    'tabContainer$TabPanel2$ddlCoreTerms': '201601',
    'tabContainer$TabPanel2$ddlCoreAreas': 'CPFA',
    'tabContainer$TabPanel2$ddlCoreSubj': 'AMST',
    'tabContainer$TabPanel3$ddlAdvTerms': '201601',
    'tabContainer$TabPanel3$ddlAdvSubj': 'AMST',
    'tabContainer$TabPanel3$ddlAdvTimes': '07000755',
    'tabContainer$TabPanel3$ddlAdvDays': 'u',
    'tabContainer$TabPanel4$ddlCRNTerms': '201601',
    'tabContainer$TabPanel4$txtCRN': '',
    'tabContainer$TabPanel5$ddlMajorsTerm': '201601',
    'tabContainer$TabPanel5$ddlCatalogYear': '201401',
    '__ASYNCPOST': 'true',
    'tabContainer$TabPanel1$btnGo': 'Go'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
}

# for key in data:
#     print(f"{key}: {data[key]}")

if caching:
    if path.exists('cached_response'):
        print('Found pre-existing response data, loading that in')
        with open('cached_response', 'r') as responseData:
            request = responseData.read()
        response = BeautifulSoup(request, 'lxml')
    else:
        print('Did not find cached response. Creating it now for next iteration')
        request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
        with open('cached_response', 'w') as responseData:
            responseData.write(request.text)
        response = BeautifulSoup(request.text, 'html.parser')
else:
    print("Starting request for all classes to server. This will take ~15 seconds to complete")
    request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
    response = BeautifulSoup(request.text, 'html.parser')
    print("Finished getting response")

semesters = response.find("select", {"name": """tabContainer$TabPanel1$ddlSemesters"""}).findAll("option")

with open("semesters.json", "w") as schools:
    for semester in semesters:
        print(semester)
        # Since oxy also uses the next near as the semester code (ex: 202201 for 2021 Fall Semester), subtract one hunred to decrement the year by one to get the correct information
        schools.write(f'{semester["value"]}\n')
        # Since all semesters will be available (even semesters that havent started yet) stop when the selected semester starts
        if semester.has_attr("selected"):
            break
