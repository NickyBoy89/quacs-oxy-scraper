import requests, json, re, sys
from bs4 import BeautifulSoup
from tqdm import tqdm

import concurrent.futures

if (len(sys.argv) > 1):
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

termYears = [str(int(term[:4]) - 1), term[:4]] # Get the academic year based on the term code (ex: 2019-2020)

if (int(termYears[0]) < 2018):
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Courses'
else:
    url = f'https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Course-Descriptions'

print(url)

def parseClassSite(url):

    result = {}

    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')

    courseTitle = soup.find('div', {'id': 'main'}).findNext('h1').findNext('span').text.replace(' ', '-')
    subj = re.search('[^-]*', courseTitle).group(0)
    crse = courseTitle[-3:]
    name = soup.find('div', {'id': 'main'}).findNext('h1').contents[2].strip()
    description = soup.find('div', {'id': 'main'}).findNext('div').findNext('p').text

    result['subj'] = subj
    result['crse'] = crse
    result['name'] = name
    result['description'] = description

    return courseTitle, result

def getMainElementsOfUrl(url):

    data = []

    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')

    for i in soup.find('div', {'id': 'main'}).findNext('ul').findChildren('li'):
        data.append(i.find('a'))

    return data

dump = {}

for i in tqdm(getMainElementsOfUrl(url)):

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:

            future_to_url = {executor.submit(parseClassSite, f"https://oxy.smartcatalogiq.com{j['href']}"): j for j in getMainElementsOfUrl(f"https://oxy.smartcatalogiq.com{i['href']}")}

            for future in concurrent.futures.as_completed(future_to_url):
                data = future.result()

                dump[data[0]] = data[1] # Returns from tuple

# print(parseClassSite('https://oxy.smartcatalogiq.com/2019-2020/Catalog/Course-Descriptions/ARAB-Arabic/200/ARAB-202'))

# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"catalog.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
