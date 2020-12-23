import requests, json, re, sys
from bs4 import BeautifulSoup
from tqdm import tqdm

import concurrent.futures

if (len(sys.argv) > 1):
    term = sys.argv[1]
else:
    with open("../semesters/semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

termYears = [str(int(term[:4]) - 1), term[:4]] # Get the academic year based on the term code (ex: 2019-2020)

if (int(termYears[0]) < 2018):
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Courses'
else:
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Course-Descriptions'

print(url)

def getMainElementsOfUrl(url):

    data = []

    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')

    for i in soup.find('div', {'id': 'main'}).findNext('ul').findChildren('li'):
        data.append(i.find('a'))

    return data

def addDepartment(department):
    return {

    }

schools = []

for i in getMainElementsOfUrl(url):
    school = i.text.split("-")
    schools.append({
        "name": school[1].strip(),
        "depts": [
            {
                "code": school[0].strip(),
                "name": school[1].strip()
            }
        ]
    })


# print(schools)

with open(f"schools.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(schools, outfile, sort_keys=False, indent=2)
