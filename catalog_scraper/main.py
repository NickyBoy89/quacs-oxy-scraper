import requests, sys
from bs4 import BeautifulSoup
from tqdm import tqdm

from typing import List, Tuple, Dict

"""
The `catalog_scraper` goes through the course catalog, and returns data about
each course, as well as some metadata about it

The data should be in the following JSON format, for example:
{
    "UBW-100": {
        "subj": "UBW",
        "crse": "100",
        "name": "Underwater Basket Weaving",
        "description": "This course actually exists"
    }
}
"""

# Uses threads for ~4x speedup, but sometimes times out

if len(sys.argv) > 1:
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        term = semesters.read().split("\n")[-2]

catalogRoot = "https://oxy.smartcatalogiq.com"

termYears = [
    str(int(term[:4]) - 1),
    term[:4],
]  # Get the academic year based on the term code (ex: 2019-2020)

# The format for the catalogs is different for years older than 2018
if int(termYears[0]) < 2018:
    url = f"https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Courses"
else:
    url = f"https://oxy.smartcatalogiq.com/en/{termYears[0]}-{termYears[1]}/Catalog/Course-Descriptions"

print(url)

"""
getMajorsFromHomepage takes in a URL from the main page of the course catalog,
and returns a list of the resulting links to the majors of the format:

Ex:
{"UBW - Underwater Basket Weaving": "/majors/courses/UBW"}
"""


def getMajorsFromHomepage(url: str) -> Dict[str, str]:
    soup = BeautifulSoup(requests.get(url=url).text.encode("UTF-8"), "lxml")

    majors: Dict[str, str] = {}

    # Make sure there are at least some links
    majorLinks = soup.find("div", {"id": "main"})
    if majorLinks != None:
        for link in majorLinks.findNext("ul").findChildren("li"):
            majors[link.find("a").get_text()] = link.find("a")["href"]

    return majors


"""
getClassesFromMajor takes in the URL of a specific major, and returns all the
metadata associated with the classes contained within
"""


def getClassesFromMajor(url: str) -> List[Tuple[str, Dict[str, str]]]:
    soup = BeautifulSoup(requests.get(url=url).text.encode("UTF-8"), "lxml")

    classes: Dict[str, str] = {}

    # Make sure there are at least some links
    classLinks = soup.find("div", {"id": "main"})
    if classLinks != None:
        for link in classLinks.findNext("ul").findChildren("li"):
            classes[link.find("a").get_text()] = link.find("a")["href"]

    return classes


"""
getDataFromClass takes in the URL for a class and returns any metadata needed
from its page

Currently, this only includes the course's description
"""


def getDataFromClass(url: str) -> Dict[str, str]:
    soup = BeautifulSoup(requests.get(url=url).text.encode("UTF-8"), "lxml")

    metadata: Dict[str, str] = {}

    metadata["description"] = soup.find("div", {"class": "desc"}).get_text().strip()

    return metadata


course_catalog = {}

for majorURL in tqdm(getMajorsFromHomepage(url).values()):
    for fullClassName, classURL in tqdm(
        getClassesFromMajor(catalogRoot + majorURL).items(), leave=False
    ):
        metadata = getDataFromClass(catalogRoot + classURL)

        # fullClassName is a string that looks like:
        # Ex: "UBW 100 Intruduction to Basketweaving"
        courseMajor, courseCode, *courseName = fullClassName.split(" ")

        metadata["subj"] = courseMajor
        metadata["crse"] = courseCode
        # This leaves courseName as a list of all the other words in the course's
        # name, so we want to put them all together
        metadata["name"] = " ".join(courseName)

        course_catalog[f"{courseMajor}-{courseCode}"] = metadata

# Write course catalog to disk
with open(f"catalog.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(course_catalog, outfile, sort_keys=True, indent=2)
