import requests, json, re, sys
from tqdm import tqdm

# Import the script to create the mod.rs
import mod_gen as modgen

# Import the scripts that talk with course counts
import counts

# You can manually specify a semester code for the script to use
if len(sys.argv) > 1:
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

dump = [] # The array that all the json data is going to be put into

# Load all the subjects in to the array
for subject in counts.subjects():
    dump.append({'name': subject.text, 'code': subject['value'], 'courses': []})

# Maps the course code to the course name (ex: AMST is mapped to American Studies)
codeMapping = {}

# Get the course catalog data to get some of the things that we have already generated
with open('catalog.json') as catalogjson:
    catalogData = json.load(catalogjson)

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

# Parses the raw HTML from each class row
def getClassDataFromRow(data):
    # All the data is stored in tds nested in the html
    tds = data.findAll('td')

    # Get the name of the course (ex: WRD 301 0), which contains the subject, the course code, and section number
    courseName = tds[1].text
    # Split the name into its three parts
    nameParts = courseName.split(" ")
    subj = nameParts[0] # Subject (ex: WRD)
    crse = nameParts[1] # Course code (ex: 301)
    sec = nameParts[2] # Section number (ex: 0)
    crn = tds[0].findChildren('a', recursive=False)[0].text

    # Get enrollment numbers
    maxSeats = tds[-5].text
    enrl = tds[-4].text

    # If section number is one digit, then append a zero to the front
    # Ex: 1 -> 01
    try:
        if int(sec) < 10:
            sec = '0' + sec
    except:
        pass
    credMin = tds[3].text
    credMax = tds[3].text
    title = tds[2].text
    # No attribute or description
    attribute = ''
    description = ''

    # A list of all days that the class is on (ex: ['M', 'W', 'F'])
    days = []

    timeslots = {
        'days': days,
        'instructor': 'Instructor-TBD',
        'location': '',
    }

    # If there is a professor specified (not TBD)
    if data.find('abbr') != None:
        timeslots['instructor'] = data.find('abbr')['title']

    timingData = []
    if data.find('table', {'cellpadding': '2'}) != None:
        # Timing data gives the times in the first element, and the days in the second
        timingData = data.find('table', {'cellpadding': '2'}).findAll('td')
        # If the days is TBD, keep it as an empty list
        if timingData[1].text != "Days-TBD":
            # Go over the days and add them to days (ex: MWF -> ['M', 'W', 'F'])
            timeslots['timeStart'] = timeToMilitary(timingData[0].text, True)
            timeslots['timeEnd'] = timeToMilitary(timingData[0].text, False)
            for day in timingData[1].text:
                days.append(day)



    if term[-2:] == "01": # Fall
        timeslots["dateStart"] = "8/24"
        timeslots["dateEnd"] = "11/20"
    elif term[-2:] == "02": # Spring
        timeslots["dateStart"] = "1/19"
        timeslots["dateEnd"] = "4/27"
    elif term[-2:] == "03": # Summer
        timeslots["dateStart"] = "5/1"
        timeslots["dateEnd"] = "8/6"

    return {
        "crn": crn,
        "subj": subj,
        "crse": crse,
        "sec": sec,
        "credMin": credMin,
        "credMax": credMax,
        "maxSeats": maxSeats,
        "enrolled": enrl,
        "title": title,
        "attribute": attribute,
        "timeslots": timeslots,
    }

# Formats the parsed class row data into the final format
def addCourse(course):
    return {
        "crn": int(course["crn"]),
        "subj": course["subj"],
        "crse": course["crse"],
        "sec": course["sec"],
        "credMin": int(course["credMin"]),
        "credMax": int(course["credMax"]),
        "title": course["title"],
        # Capacity of the course
        "cap": int(course["maxSeats"]),
        # Seats accounted for
        "act": int(course["enrolled"]),
        # Remaining seats (capacity - act) if there isn't any overassignment
        "rem": int(course["maxSeats"]) - int(course["enrolled"]),
        "attribute": course["attribute"],
        "timeslots": [course["timeslots"]]
    }

# Puts the raw data from each row into json format
def insertClassDataIntoJson(rowData):
    classData = getClassDataFromRow(rowData)
    # Go through the generated JSON to find the department to add the course to
    for department in enumerate(dump):
        # Test if class is in current department
        if (department[1]["code"] == classData["subj"]):
            # True if course is found in the courses
            courseFound = False

            # Tests to see if the course already exists, if it does, insert the class as a section
            for course in enumerate(department[1]["courses"]):
                if (course[1]["title"] == classData["title"]):
                    courseFound = True
                    dump[department[0]]["courses"][course[0]]["sections"].append(addCourse(classData))

            if not courseFound:
                # Generate new course if not found
                dump[department[0]]['courses'].append({
                    "title": classData["title"],
                    "subj": classData["subj"],
                    "crse": classData["crse"],
                    "id": classData["subj"] + "-" + classData["crse"],
                    "sections": [addCourse(classData)]
                })

response = counts.allCourses(True, term)

print("Going through courses")
# Go through all the rows in the response and load them into JSON
for i in (response.findAll('tr', {'style': 'background-color:#C5DFFF;font-size:X-Small;'}) + response.findAll('tr', {'style': 'background-color:White;font-size:X-Small;'})):
    insertClassDataIntoJson(i)
print("Done going through courses")

# Generate the mod.rs file from the data
print("Generating mod.rs")
modgen.genmod(dump, None)
print("Done generating mod.rs")

# Saving data into json file
# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"courses.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
