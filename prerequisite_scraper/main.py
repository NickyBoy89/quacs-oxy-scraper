import requests, json, re, time, sys
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import path
import urllib3

import concurrent.futures

import prereq_parser as prereq

# The number of workers to use when making the requests to the server
concurrentWorkers = 4

# Ignore the SSL errors
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if len(sys.argv) > 1:
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

caching = False  # Set this to True to cache the ~15s long initial request to the server

dump = {}  # Stores the final JSON generated

session = requests.Session()  # Initialize the browser session

# Load the homepage and get its data into a session
initialLoad = session.get("https://counts.oxy.edu/public/default.aspx", verify=False)
soup = BeautifulSoup(initialLoad.text, "html.parser")

# Extracts data from class page
def getClassPageData(data, sessionData, threadNumber, verbose=False):
    # print(f"Started thread {threadNumber}")

    classButton = data.find("a")["href"][25:-5]

    postData = {
        "ScriptManager2": f"searchResultsPanel|{classButton}",
        "tabContainer$TabPanel1$ddlSemesters": term,
        "tabContainer$TabPanel1$ddlSubjects": "",
        "tabContainer$TabPanel1$txtCrseNum": "",
        "tabContainer$TabPanel2$ddlCoreTerms": "201601",
        "tabContainer$TabPanel2$ddlCoreAreas": "CPFA",
        "tabContainer$TabPanel2$ddlCoreSubj": "AMST",
        "tabContainer$TabPanel3$ddlAdvTerms": "201601",
        "tabContainer$TabPanel3$ddlAdvSubj": "AMST",
        "tabContainer$TabPanel3$ddlAdvTimes": "07000755",
        "tabContainer$TabPanel3$ddlAdvDays": "u",
        "tabContainer$TabPanel4$ddlCRNTerms": "201601",
        "tabContainer$TabPanel4$txtCRN": "",
        "tabContainer$TabPanel5$ddlMajorsTerm": "201601",
        "tabContainer$TabPanel5$ddlCatalogYear": "200801",
        "__EVENTTARGET": classButton,
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": re.findall("(?<=(\|__VIEWSTATE\|))(.*?)(?=\|)", response.text)[
            0
        ][1],
        "__VIEWSTATEGENERATOR": re.findall(
            "(?<=(\|__VIEWSTATEGENERATOR\|))(.*?)(?=\|)", response.text
        )[0][1],
        "__EVENTVALIDATION": re.findall(
            "(?<=(\|__EVENTVALIDATION\|))(.*?)(?=\|)", response.text
        )[0][1],
        "tabContainer_ClientState": """{"ActiveTabIndex":0,"TabEnabledState":[true,true,true,true,true],"TabWasLoadedOnceState":[true,false,false,false,false]}""",
        "__VIEWSTATEENCRYPTED": re.findall(
            "(?<=(\|__VIEWSTATEENCRYPTED\|\|))(.*?)(?=\|)", response.text
        )[0][1],
        "__ASYNCPOST": "true",
    }
    postHeaders = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    }
    postResponse = sessionData.post(
        url="https://counts.oxy.edu/public/default.aspx",
        data=postData,
        headers=postHeaders,
    )
    classSoup = BeautifulSoup(postResponse.text, "lxml")
    if verbose:
        print(classSoup.find("span", {"id": "lblCrseDesc"}))

    restrictionsPanel = ""
    corequisitesPanel = ""
    prereqsPanel = ""
    reservedPanel = ""

    if classSoup.find(id="restrictionsPanel") != None:
        restrictionsPanel = (
            classSoup.find(id="restrictionsPanel").findNext("ul").findAll("li")
        )

    if classSoup.find(id="corequisitesPanel") != None:
        corequisitesPanel = (
            classSoup.find(id="corequisitesPanel").findNext("span").text.split(", ")
        )
        for i in range(len(corequisitesPanel)):
            corequisitesPanel[i] = joinFirstTwoWordsWithDash(corequisitesPanel[i])

    if classSoup.find(id="prereqsPanel") != None:
        prereqsPanel = parsePrerequisites(
            classSoup.find(id="prereqsPanel").findAll("tr")[1:]
        )

    if classSoup.find(id="resvDetailsPanel") != None:
        reservedPanel = parseReservedSeats(
            classSoup.find(id="resvDetailsPanel").findAll("tr")[1:]
        )

    if data.find("a") != None:
        textKey = data.find("a").text

    if verbose:
        print(f"Prerequitites: {prereqsPanel}")
        print(f"Corequisites: {corequisitesPanel}")
        print(f"Restrictions: {restrictionsPanel}")

    # print(f"Finished thread {threadNumber}")

    return {
        "restrictions": restrictionsPanel,
        "coreqs": corequisitesPanel,
        "prereqs": prereqsPanel,
        "reserved": reservedPanel,
        "textKey": textKey,
    }


def joinFirstTwoWordsWithDash(words):
    return re.findall("([^\s]+\s+[^\s]+)", words)[0].replace(" ", "-")


def getLevelRestriction(listText):
    restrictions = {"may_not_be": []}
    for level in listText:
        if "students may not enroll in this class" in level.text:
            restrictions["may_not_be"] = getPrereqRestriction(
                re.findall(".+?(?= students may not enroll in this class)", level.text)[
                    0
                ]
            )
        elif "students may enroll in this class" in level.text:
            restrictions["must_be"] = getPrereqRestriction(
                re.findall(".+?(?= students may enroll in this class)", level.text)[0]
            )
    return restrictions


# Restrictions panel
def getPrereqRestriction(listText):
    levels = []
    if "Graduate" in listText:
        levels.append("Graduate")
    if "Senior" in listText:
        levels.append("Senior")
    if "Junior" in listText:
        levels.append("Junior")
    if "Frosh" in listText:
        levels.append("Frosh")
    return levels


# Parses a list of rows from the reserved seats section and returns a list of dictionaries with the corresponding mappings:
# "reservedFor" - who the class is reserved for, "max" - Number of seats reserved, and "open" - the number of reserved seats left
def parseReservedSeats(reservedSeatRows):
    parsedReservations = []
    for row in reservedSeatRows:
        currentReservation = {}
        for index, item in enumerate(row.findAll("td")):
            if index == 0:  # First item is reservedFor
                currentReservation["reservedFor"] = item.text
            elif index == 1:
                currentReservation["max"] = int(item.text)
            elif index == 2:
                currentReservation["open"] = int(item.text)
        parsedReservations.append(currentReservation)
    return parsedReservations


# Parenthesies stripping logic
def parsePrerequisites(prereqList):
    returnPrereqs = []
    groupedLogic = []
    insideGroup = False
    pareIndex = {"(": [], ")": []}
    for i in prereqList:
        returnPrereqs.append(i.find("td").text)
    for prerequisite in range(len(returnPrereqs)):
        if (
            "(" in returnPrereqs[prerequisite]
        ):  # Note: Does not work with nested parenthesies
            returnPrereqs[prerequisite] = returnPrereqs[prerequisite][
                1:
            ].strip()  # Strip out the opening parenthesies
            pareIndex["("].append(prerequisite)
            insideGroup = True
        elif ")" in returnPrereqs[prerequisite]:
            returnPrereqs[prerequisite] = returnPrereqs[prerequisite][
                :-1
            ].strip()  # Strip out the closing parenthesies
            pareIndex[")"].append(prerequisite)
            if insideGroup == True:
                groupedLogic.append(
                    returnPrereqs[(pareIndex["("][0]) : (pareIndex[")"][0])]
                )
                del pareIndex["("][0]
                del pareIndex[")"][0]
            insideGroup = False
        elif insideGroup == False:
            groupedLogic.append(returnPrereqs[prerequisite])
    # print(groupedLogic)
    return returnPrereqs


# Parses the data that comes from getClassPageData into JSON
def parseJson(data):
    finalRestrictions = {}

    if len(data["restrictions"]) > 0:
        finalRestrictions["restrictions"] = {}
        finalRestrictions["restrictions"]["classification"] = getLevelRestriction(
            data["restrictions"]
        )
    if len(data["coreqs"]) > 0:
        finalRestrictions["corequisites"] = {}
        finalRestrictions["corequisites"]["cross_list_courses"] = data["coreqs"]
    if len(data["prereqs"]) > 0:
        finalRestrictions["prerequisites"] = prereq.parse(data["prereqs"])
    if len(data["reserved"]) > 0:
        finalRestrictions["reserved"] = data["reserved"]

    # print(finalRestrictions)
    return finalRestrictions


data = {
    "ScriptManager2": """pageUpdatePanel|tabContainer$TabPanel1$btnGo""",
    "tabContainer_ClientState": soup.find(id="tabContainer_ClientState")["value"],
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__LASTFOCUS": "",
    "__VIEWSTATE": soup.find(id="__VIEWSTATE")["value"],
    "__VIEWSTATEGENERATOR": soup.find(id="__VIEWSTATEGENERATOR")["value"],
    "__VIEWSTATEENCRYPTED": soup.find(id="__VIEWSTATEENCRYPTED")["value"],
    "__EVENTVALIDATION": soup.find(id="__EVENTVALIDATION")["value"],
    "tabContainer$TabPanel1$ddlSemesters": term,
    "tabContainer$TabPanel1$ddlSubjects": "",
    "tabContainer$TabPanel1$txtCrseNum": "",
    "tabContainer$TabPanel2$ddlCoreTerms": "201601",
    "tabContainer$TabPanel2$ddlCoreAreas": "CPFA",
    "tabContainer$TabPanel2$ddlCoreSubj": "AMST",
    "tabContainer$TabPanel3$ddlAdvTerms": "201601",
    "tabContainer$TabPanel3$ddlAdvSubj": "AMST",
    "tabContainer$TabPanel3$ddlAdvTimes": "07000755",
    "tabContainer$TabPanel3$ddlAdvDays": "u",
    "tabContainer$TabPanel4$ddlCRNTerms": "201601",
    "tabContainer$TabPanel4$txtCRN": "",
    "tabContainer$TabPanel5$ddlMajorsTerm": "201601",
    "tabContainer$TabPanel5$ddlCatalogYear": "200801",
    "__ASYNCPOST": "true",
    "tabContainer$TabPanel1$btnGo": "Go",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}

# Gets all the course information and turns it into a soup, plus some pseudo-caching logic to speed up development
if caching:
    if path.exists("cached_response"):
        print("Found pre-existing response data, loading that in")
        with open("cached_response", "r") as responseData:
            request = responseData.read()
        response = BeautifulSoup(request, "lxml")
    else:
        print("Did not find cached response. Creating it now for next iteration")
        request = session.post(
            "https://counts.oxy.edu/public/default.aspx",
            data=data,
            headers=headers,
            verify=False,
        )
        with open("cached_response", "w") as responseData:
            responseData.write(request.text)
        response = BeautifulSoup(request.text, "html.parser")
else:
    print(
        "Starting request for all classes to server. This will take ~15 seconds to complete"
    )
    request = session.post(
        "https://counts.oxy.edu/public/default.aspx",
        data=data,
        headers=headers,
        verify=False,
    )
    response = BeautifulSoup(request.text, "html.parser")
    print("Finished getting response")

start = time.time()

# Finds all classes by rows
classRows = response.findAll(
    "tr", {"style": "background-color:#C5DFFF;font-size:X-Small;"}
) + response.findAll("tr", {"style": "background-color:White;font-size:X-Small;"})

# Multithreading
if concurrentWorkers <= 1:
    for ind, i in tqdm(enumerate(classRows)):
        data = getClassPageData(i, session, ind)
        dump[data["textKey"]] = parseJson(data)
else:
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=concurrentWorkers
    ) as executor:
        # Submit all the work to the thread pool
        future_to_url = {
            executor.submit(getClassPageData, i[1], session, i[0], verbose=False): i
            for i in enumerate(classRows)
        }
        # Collect the results
        for future in tqdm(
            concurrent.futures.as_completed(future_to_url), total=len(classRows)
        ):
            data = future.result()
            dump[data["textKey"]] = parseJson(data)

# Saving data into json file
# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"prerequisites.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=True, indent=2)

print(time.time() - start)
