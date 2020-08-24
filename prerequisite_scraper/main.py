import requests, json, re
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import path

caching = False # Set this to true to drastically speed up requests for local development (NOTE: Must be run once to be cached)

dump = {} # The dict that all the json data is going to come from

session = requests.Session() # Initialize the browser session

# Load the homepage and get its data
initialLoad = session.get('https://counts.oxy.edu/public/default.aspx', verify=False)
soup = BeautifulSoup(initialLoad.text, 'html.parser')

# Breakpoint before long request
# quit()

def getClassPageData(classButton, sessionData):
    postData = {
        'ScriptManager2': f'searchResultsPanel|{classButton}',
        'tabContainer$TabPanel1$ddlSemesters': '202101',
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
        'tabContainer$TabPanel5$ddlCatalogYear': '201601',
        '__EVENTTARGET': 'gvResults$ctl02$lnkBtnCrn',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': re.findall('(?<=(\|__VIEWSTATE\|))(.*?)(?=\|)', response.text)[0][1],
        '__VIEWSTATEGENERATOR': re.findall('(?<=(\|__VIEWSTATEGENERATOR\|))(.*?)(?=\|)', response.text)[0][1],
        '__EVENTVALIDATION': re.findall('(?<=(\|__EVENTVALIDATION\|))(.*?)(?=\|)', response.text)[0][1],
        'tabContainer_ClientState': """{"ActiveTabIndex":0,"TabEnabledState":[true,true,true,true,true],"TabWasLoadedOnceState":[true,false,false,false,false]}""",
        '__VIEWSTATEENCRYPTED': re.findall('(?<=(\|__VIEWSTATEENCRYPTED\|\|))(.*?)(?=\|)', response.text)[0][1],
        '__ASYNCPOST': 'true'
    }
    postHeaders = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
    }
    postResponse = sessionData.post(url='https://counts.oxy.edu/public/default.aspx', data=postData, headers=postHeaders)
    classSoup = BeautifulSoup(postResponse.text, 'lxml')

    resvDetailsPanel = ''
    restrictionsPanel = ''
    corequisitesPanel = ''
    prereqsPanel = ''


    if classSoup.find(id='resvDetailsPanel') != None:
        resvDetailsPanel = classSoup.find(id='resvDetailsPanel').find('div').findAll('tr')[1:]
        print(resvDetailsPanel)
    if classSoup.find(id='restrictionsPanel') != None:
        restrictionsPanel = classSoup.find(id='restrictionsPanel').findNext('ul').findAll('li')
        for restriction in range(len(restrictionsPanel)):
            restrictionsPanel[restriction] = re.findall('^([\w\-]+)', restrictionsPanel[restriction].text)
        print(restrictionsPanel)
    if classSoup.find(id='corequisitesPanel') != None:
        corequisitesPanel = classSoup.find(id='corequisitesPanel').findNext('ul').findAll('li')
        print(corequisitesPanel)
    if classSoup.find(id='prereqsPanel') != None:
        prereqsPanel = classSoup.find(id='prereqsPanel').findNext('ul').findAll('li')
        print(prereqsPanel)
    # resvDetailsPanel
    # restrictionsPanel
    # corequisitesPanel
    # prereqsPanel

    # re.findall('^([\w\-]+)', resvDetailsPanel.text)

    return({'reservations': resvDetailsPanel, 'restrictions': restrictionsPanel, 'corequisites': corequisitesPanel, 'prerequisites': prereqsPanel})



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
    'tabContainer$TabPanel1$ddlSemesters': '202101',
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
    'tabContainer$TabPanel5$ddlCatalogYear': '201601',
    '__ASYNCPOST': 'true',
    'tabContainer$TabPanel1$btnGo': 'Go'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
}


# Gets all the course information and turns it into a soup, plus some pseudo-caching logic to speed up development

if caching:
    if path.exists('responseData.txt'):
        print('Found pre-existing response data, loading that in')
        with open('responseData.txt', 'r') as responseData:
            request = responseData.read()
        response = BeautifulSoup(request, 'lxml')
    else:
        print('Did not find cached response. Creating it now for next iteration')
        request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
        with open('responseData.txt', 'w') as responseData:
            responseData.write(request.text)
        response = BeautifulSoup(request.text, 'html.parser')
else:
    request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
    response = BeautifulSoup(request.text, 'html.parser')


testClass = (response.findAll('tr', {'style': 'background-color:#C5DFFF;font-size:X-Small;'}) + response.findAll('tr', {'style': 'background-color:White;font-size:X-Small;'}))[0]

# print(testClass.find('a')['href'][25:-5])

# getClassPageData(session)

for i in tqdm((response.findAll('tr', {'style': 'background-color:#C5DFFF;font-size:X-Small;'}) + response.findAll('tr', {'style': 'background-color:White;font-size:X-Small;'}))[:10]):
    dump[i.find('a').text] = getClassPageData(i.find('a')['href'][25:-5], session)



# print(dump)




# Saving data into json file
print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"prerequisites.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
