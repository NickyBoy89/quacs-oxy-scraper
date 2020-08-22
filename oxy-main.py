import requests, json
from bs4 import BeautifulSoup

session = requests.Session()

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
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Length': '22144',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Host': 'counts.oxy.edu',
    'Origin': 'https://counts.oxy.edu',
    'Pragma': 'no-cache',
    'Referer': 'https://counts.oxy.edu/public/default.aspx',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36',
    'X-MicrosoftAjax': 'Delta=true',
    'X-Requested-With': 'XMLHttpRequest'
}

request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
# print(request.text)
response = BeautifulSoup(request.text, 'html.parser')

dump = {}

def stripClass(data, storage):
    courseName = data.findAll('td')[1].text
    subj = data.findAll('td')[1].text[:5]
    crse = data.find('td').findChildren('a', recursive=False)[0].text
    name = data.findAll('td')[2].text
    description = 'None'
    storage[courseName] = {}
    storage[courseName]['subj'] = subj
    storage[courseName]['crse'] = crse
    storage[courseName]['name'] = name
    storage[courseName]['description'] = description
    return([courseName, subj, crse, name, description])

# print(response)
for i in (response.findAll('tr', {'style': 'background-color:#C5DFFF;font-size:X-Small;'}) + response.findAll('tr', {'style': 'background-color:White;font-size:X-Small;'})):
    print(stripClass(i, dump))

print(dump)
print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"catalog.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
