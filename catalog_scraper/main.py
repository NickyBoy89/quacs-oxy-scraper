import requests, json
from bs4 import BeautifulSoup
from tqdm import tqdm

url = 'https://oxy.smartcatalogiq.com/en/2019-2020/Catalog/Course-Descriptions'

def parseClassSite(url, dump):

    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')

    courseTitle = soup.find('div', {'id': 'main'}).findNext('h1').findNext('span').text.replace(' ', '-')
    subj = courseTitle[:4]
    crse = courseTitle[-3:]
    name = soup.find('div', {'id': 'main'}).findNext('h1').contents[2].strip()
    description = soup.find('div', {'id': 'main'}).findNext('div').findNext('p').text

    dump[courseTitle] = {}
    dump[courseTitle]['subj'] = subj
    dump[courseTitle]['crse'] = crse
    dump[courseTitle]['name'] = name
    dump[courseTitle]['description'] = description

    return([courseTitle, subj, crse, name, description])

def getMainElementsOfUrl(url):

    data = []

    soup = BeautifulSoup(requests.get(url=url).text.encode('UTF-8'), 'lxml')

    for i in soup.find('div', {'id': 'main'}).findNext('ul').findChildren('li'):
        data.append(i.find('a'))

    return(data)

dump = {}

for i in getMainElementsOfUrl(url):
    # print(i)
    for j in tqdm(getMainElementsOfUrl(f"https://oxy.smartcatalogiq.com{i['href']}")):
        # print(getMainElementsOfUrl(f'https://oxy.smartcatalogiq.com{j}'))
        # print(j)
        for k in parseClassSite(f"https://oxy.smartcatalogiq.com{j['href']}", dump):
            # print(k)
            pass
    # print(i.text)
    # for j in getMainElementsOfUrl(i['href'])

# print(parseClassSite('https://oxy.smartcatalogiq.com/2019-2020/Catalog/Course-Descriptions/ARAB-Arabic/200/ARAB-202'))

print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"catalog.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=False, indent=2)
