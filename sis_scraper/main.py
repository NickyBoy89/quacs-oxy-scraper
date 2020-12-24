import requests, json, re, urllib3, sys
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import path

# Import the scrip to create the mod.rs

import mod_gen as modgen

# Ignore the SSL errors

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if (len(sys.argv) > 1):
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

caching = False # Set this to true to drastically speed up requests for local development (NOTE: Must be run once to be cached)

dump = [] # The array that all the json data is going to be put into

session = requests.Session() # Initialize the browser session

# Load the homepage and get its data
print("Starting request")
initialLoad = session.get('https://counts.oxy.edu/public/default.aspx', verify=False)
soup = BeautifulSoup(initialLoad.text, 'html.parser')
print("Finished request")

# Maps the course code to the course name (ex: AMST is mapped to American Studies)
codeMapping = {}

# Populate the dump variable with the departments
for i in soup.find(id='tabContainer_TabPanel3_ddlAdvSubj').findAll('option'):
    codeMapping[i['value']] = i.text
    dump.append({'name': i.text, 'code': i['value'], 'courses': []})

# Breakpoint before long request
# quit()

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
    'tabContainer$TabPanel1$ddlSemesters': term,
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
    print("Starting request for all classes to server. This will take ~15 seconds to complete")
    request = session.post("https://counts.oxy.edu/public/default.aspx", data=data, headers=headers, verify=False)
    response = BeautifulSoup(request.text, 'html.parser')
    print("Finished getting response")

# Get the course catalog data to get some of the things that we have already generated
with open('catalog.json') as catalogjson:
    catalogData = json.load(catalogjson)

# quit()

throwaway = {}

def timeToMilitary(time, useStartTime):
    if "TBD" in time:
        return -1
    if useStartTime:
        time = time.split("-")[0]
    else:
        time = time.split("-")[1]

    offset = 0
    if "pm" in time and "12:" not in time:
        offset = 1200
    return int("".join(time.strip().split(":"))[:4]) + offset

def getClassDataFromRow(data, storage):
    days = []

    courseName = data.findAll('td')[1].text
    subj = re.match('([^\s]+)', data.findAll('td')[1].text).group()
    crn = data.find('td').findChildren('a', recursive=False)[0].text
    crse = re.findall('([^\s]+)', data.findAll('td')[1].text)[1]
    sec = re.findall('([^\s]+)', data.findAll('td')[1].text)[2]
    try:
        if int(sec) < 10:
            sec = '0' + sec
    except:
        pass
    credMin = data.findAll('td')[3].text
    credMax = data.findAll('td')[3].text
    title = data.findAll('td')[2].text
    attribute = ''
    description = ''
    timingData = data.find('table', {'cellpadding': '2'}).findAll('td')
    for day in timingData[1].text:
        days.append(day)
    timeslots = [{'days': days, 'timeStart': timeToMilitary(timingData[0].text, True), 'timeEnd': timeToMilitary(timingData[0].text, False), 'instructor': data.find('abbr')['title'], 'dateStart': '8/24', 'dateEnd': '11/20', 'location': ''}]


    storage[courseName] = {}
    storage[courseName]['crn'] = int(crn) # Course crn (ex: 1001)
    storage[courseName]['subj'] = subj # Course number (ex: AMST)
    storage[courseName]['crse'] = crse # Course number (ex: 201)
    storage[courseName]['title'] = title # Course name (ex: Introduction to American Studies)
    storage[courseName]['description'] = description # Description

    return([crn, subj, crse, sec, credMin, credMax, title, attribute, timeslots])

def addCourse(course):
    return {
        "crn": int(course[0]),
        "subj": course[1],
        "crse": course[2],
        "sec": course[2],
        "credMin": int(course[4]),
        "credMax": int(course[5]),
        "title": course[6],
        "attribute": course[7],
        "timeslots": course[8]
    }

def insertClassDataIntoJson(rowData):

    classData = getClassDataFromRow(rowData, throwaway)
    # print(classData)

    for department in enumerate(dump):

        # print(department[1])

        # Test if class is in current department
        if (department[1]['code'] == classData[1]):

            # True if course is found in the courses
            courseFound = False

            # Tests to see if the course is already in the courses
            for course in enumerate(department[1]["courses"]):
                if (course[1]["title"] == classData[6]):

                    courseFound = True

                    dump[department[0]]["courses"][course[0]]["sections"].append(addCourse(classData))

            if (not courseFound):

                # Generate new course if not found
                dump[department[0]]['courses'].append({
                    "title": classData[6],
                    "subj": classData[1],
                    "crse": classData[0],
                    "id": f"{classData[1]}-{classData[2]}",
                    "sections": [addCourse(classData)]
                })

for i in (response.findAll('tr', {'style': 'background-color:#C5DFFF;font-size:X-Small;'}) + response.findAll('tr', {'style': 'background-color:White;font-size:X-Small;'})):
    insertClassDataIntoJson(i)

# Generate the mod.rs file from the data

modgen.genmod(dump, None)

# Saving data into json file
# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"courses.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
