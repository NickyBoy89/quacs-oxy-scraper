import requests, json, re, sys
from bs4 import BeautifulSoup
from tqdm import tqdm

import concurrent.futures

# Some default custom groupings that I thought were fitting to reduce the number of elements on the main page
school_groupings = {
    "Foreign Languages and Studies": [
        "Arabic",
        "French",
        "German",
        "Greek",
        "Russian",
        "Japanese Studies",
        "Spanish",
        "Latin",
        "Latino/a and Latin American Studies",
        "East Asian Studies",
        "Chinese Studies",
    ],
    "Humanities, Arts, and Social Sciences": [
        "Studio Art",
        "Art History",
        "Media Arts and Culture",
        "Theater",
        "Music",
        "Music Applied Study",
        "Comparative Studies in Literature and Culture",
        "Economics",
        "History",
        "Philosophy",
        "Sociology",
        "Education",
        "Religious Studies",
        "Linguistics",
    ],
    "Politics and Public Relations": [
        "Diplomacy & World Affairs",
        "Politics",
    ],
    "Social Affairs": [
        "Urban & Environmental Policy",
        "Public Health",
        "Critical Theory and Social Justice",
    ],
    "Sciences": [
        "Biochemistry",
        "Biology",
        "Chemistry",
        "Geology",
        "Cognitive Science",
        "Mathematics",
        "Physics",
        "Psychology",
        "Computer Science",
        "Kinesiology",
    ],
    "Literature": [
        "English",
        "Writing & Rhetoric",
    ]
}

# For passing in a custom semester (such as through the generation script)
if (len(sys.argv) > 1):
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

termYears = [str(int(term[:4]) - 1), term[:4]] # Get the academic year based on the term code (ex: 2019-2020)

# The catalog changes format for years before 2018
if (int(termYears[0]) < 2018):
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Courses'
else:
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Course-Descriptions'

print("Scraping " + url)

# Extract the school names and acronym from the page (ex: Mathematics and MATH)
def getSchoolsFromUrl(url):
    data = []
    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')
    if soup.find('div', {'id': 'main'}) != None:
        for i in soup.find('div', {'id': 'main'}).findNext('ul').findChildren('li'):
            data.append(i.find('a'))
    return data

schools = []

for rawSchool in getSchoolsFromUrl(url):
    school = rawSchool.text.split("-") # Split out the Name from the acronym
    if len(school) < 2: # If there is a parser error, skip the schoool
        continue
    school_name = school[1].strip()
    school_code = school[0].strip()

    added = False

    # If the name of the school is in the pre-generated groupings
    for group_name in school_groupings:
        # If the name of the school is in the group
        if school_name in school_groupings[group_name]:
            if len(schools) == 0:
                schools.append({
                    "name": group_name,
                    "depts": [
                        {
                            "code": school_code,
                            "name": school_name,
                        }
                    ]
                })
                added = True
                break

            # Look through all the generated schools to find the group that has already been generated
            for generated_school in enumerate(schools):
                if generated_school[1]["name"] == group_name:
                    schools[generated_school[0]]["depts"].append({
                        "code": school_code,
                        "name": school_name,
                    })
                    added = True
                    break
            if added:
                break
            # If there is no pre-generated group found, generate it
            schools.append({
                "name": group_name,
                "depts": [
                    {
                        "code": school_code,
                        "name": school_name,
                    }
                ]
            })
            added = True
    # Add the school normally
    if not added:
        schools.append({
            "name": school_name,
            "depts": [
                {
                    "code": school_code,
                    "name": school_name,
                }
            ]
        })
    added = False


print(schools)

with open(f"schools.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(schools, outfile, sort_keys=False, indent=2)
