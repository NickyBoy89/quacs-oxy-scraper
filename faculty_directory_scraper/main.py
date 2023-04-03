import requests, json, re
from bs4 import BeautifulSoup
from tqdm import tqdm


# response = requests.get(url='https://faculty.rpi.edu/data/peoplesearch')
# soup = BeautifulSoup(response.text.encode('utf8'), "html")


def getFacultyInfo(soup):
    biography = ""
    area = ""
    education = ""

    name = soup.find("a").text  # Get name of faculty member

    url = soup.find("a")["href"]  # Get link to faculty member page

    profilePage = BeautifulSoup(
        requests.get(f"https://www.oxy.edu{url}").text.encode("UTF-8"), "lxml"
    )
    portrait = profilePage.findAll("img")[2][
        "src"
    ]  # Get faculty member photo from page

    title = (
        soup.find("div", {"class": "views-field-field-faculty-member-title"})
        .find("div")
        .text
    )  # Get faculty member's official title of work

    if (
        profilePage.find("div", {"class": "field-name-field-intro-copy"}) != None
    ):  # Check if the biography is not blank and get their short bio
        if (
            profilePage.find("div", {"class": "field-name-field-intro-copy"})
            .findNext("div")
            .findNext("div")
            .find("p")
            != None
        ):
            biography = (
                profilePage.find("div", {"class": "field-name-field-intro-copy"})
                .findNext("div")
                .findNext("div")
                .find("p")
                .text
            )
        elif (
            profilePage.find("div", {"class": "field-name-field-intro-copy"})
            .findNext("div")
            .findNext("div")
            .find("div")
            != None
        ):
            biography = (
                profilePage.find("div", {"class": "field-name-field-intro-copy"})
                .findNext("div")
                .findNext("div")
                .find("div")
                .text
            )
    if len(soup.findAll("div", {"class": "field-item even"})) > 1:
        education = soup.findAll("div", {"class": "field-item even"})[
            1
        ].text  # Get faculty member's education level

    areaField = re.compile("(?<=, ).*").search(
        title
    )  # Regex-search the faculty member's title to get their area of work
    if areaField != None:
        area = areaField.group()

    return [name, url, portrait, title, biography, education, area]


faculty = requests.get("https://www.oxy.edu/academics/faculty/faculty-index")

soup = BeautifulSoup(faculty.text.encode("UTF-8"), "lxml")

# print(soup.find('div', {'class': 'view-content'}).findAll('div', {'class': 'views-row'})[0])

# print(len(soup.find('div', {'class': 'view-content'}).findAll('div', {'class': 'views-row'})))

# print(getFacultyInfo(soup.find('div', {'class': 'view-content'}).findAll('div', {'class': 'views-row'})[1]))

data = {}

for i in tqdm(
    soup.find("div", {"class": "view-content"}).findAll("div", {"class": "views-row"})
):
    professor = getFacultyInfo(i)
    data[professor[0]] = {}
    data[professor[0]]["url"] = professor[1]
    data[professor[0]]["portrait"] = professor[2]
    data[professor[0]]["title"] = professor[3]
    data[professor[0]]["biography"] = professor[4]
    data[professor[0]]["education"] = professor[5]
    data[professor[0]]["area"] = professor[6]

with open(f"faculty.json", "w") as outfile:
    json.dump(data, outfile, sort_keys=False, indent=2)
