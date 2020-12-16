import requests

session = requests.Session() # Initialize the browser session

# Load course counts and get its data
initialLoad = session.get('https://counts.oxy.edu/public/default.aspx', verify=False)
soup = BeautifulSoup(initialLoad.text, 'html.parser')

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
        '__EVENTTARGET': classButton,
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
    print(classSoup.find('span', {'id': 'lblCrseDesc'}))

    restrictionsPanel = ''
    corequisitesPanel = ''
    prereqsPanel = ''


    if classSoup.find(id='restrictionsPanel') != None:
        restrictionsPanel = classSoup.find(id='restrictionsPanel').findNext('ul').findAll('li')
    print(f'Restrictions: {restrictionsPanel}')
    # print(classSoup.find(id='corequisitesPanel'))
    if classSoup.find(id='corequisitesPanel') != None:
        corequisitesPanel = classSoup.find(id='corequisitesPanel').findNext('span').text.split(', ')
        for i in range(len(corequisitesPanel)):
            corequisitesPanel[i] = joinFirstTwoWordsWithDash(corequisitesPanel[i])
    print(f'Corequisites: {corequisitesPanel}')
    # print(classSoup.find(id='prereqsPanel'))
    if classSoup.find(id='prereqsPanel') != None:
        prereqsPanel = parsePrerequisites(classSoup.find(id='prereqsPanel').findAll('tr')[1:])
    print(f'Prerequitites: {prereqsPanel}')
    # restrictionsPanel
    # corequisitesPanel
    # prereqsPanel

    # re.findall('^([\w\-]+)', resvDetailsPanel.text)

    return([restrictionsPanel, corequisitesPanel, prereqsPanel])
