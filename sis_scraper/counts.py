import urllib3, requests
from os import path
from bs4 import BeautifulSoup

# Ignore the SSL errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session() # Initialize the browser session

# Load the homepage and its data
print("Loading course counts")
initialLoad = session.get('https://counts.oxy.edu/public/default.aspx', verify=False)
soup = BeautifulSoup(initialLoad.text, 'html.parser')

def semesters():
    semesters = []
    for semester in soup.find(id="tabContainer_TabPanel1_ddlSemesters").findAll("option"):
        semesters.append(semester)
    return semesters

# Returns a list of subjects from the homepage
def subjects():
    semesterOptions = []
    for semesterOption in soup.find(id='tabContainer_TabPanel3_ddlAdvSubj').findAll('option'):
        semesterOptions.append(semesterOption)
    return semesterOptions

def allCourses(caching, oxySemester):
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
        'tabContainer$TabPanel1$ddlSemesters': oxySemester,
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
        'tabContainer$TabPanel5$ddlCatalogYear': '200801',
        '__ASYNCPOST': 'true',
        'tabContainer$TabPanel1$btnGo': 'Go'
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
    }

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

    return response
