import requests, sys
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

from typing import List, Tuple, Dict, Self


class CatalogUrl:
    root_url: str
    language: str = "en"
    current_year: int
    suffix: str = ""

    def __str__(self) -> str:
        return f"CatalogUrl {{ root_url: {self.root_url}, language: {self.language}, current_year: {self.current_year}, suffix: {self.suffix} }}"

    def __repr__(self) -> str:
        return self.__str__()

    def format(self) -> str:
        suffix = ""

        if self.current_year < 2018:
            suffix = "Catalog/Courses"
        elif self.current_year < 2023:
            suffix = "Catalog/Course-Descriptions"
        else:
            suffix = "catalog/course-descriptions"

        if self.suffix != "":
            suffix += "/" + self.suffix

        if self.current_year >= 2023:
            suffix = suffix.lower()

        # The year always starts with the previous year
        return f"{self.root_url}/{self.language}/{self.current_year - 1}-{self.current_year}/{suffix}"

    def parse_relative_url(self, url: str) -> Self:
        _, language, term_years, _, _, *parts = url.split("/")

        parsed_url = CatalogUrl()
        parsed_url.root_url = self.root_url
        parsed_url.language = language
        parsed_url.current_year = int(term_years.split("-")[1])

        parsed_url.suffix = "/".join(parts)

        return parsed_url


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
        # Get the last semester number, but remove the newline
        term = semesters.read().split("\n")[-2]

current_catalog_url = CatalogUrl()
current_catalog_url.language = "en"
current_catalog_url.root_url = "https://oxy.smartcatalogiq.com"

# Get the academic year based on the term code
# This is in the format of `202301`, where the first three characters are the year
# and the rest are the semester code
assert len(term) == 6

current_catalog_url.current_year = int(term[:4])

"""
`get_majors_from_homepage` takes in a URL from the main page of the course catalog,
and returns a list of the resulting links to the majors of the format:

Ex:
{"UBW - Underwater Basket Weaving": "/majors/courses/UBW"}
"""


def get_majors_from_homepage(url: CatalogUrl) -> Dict[str, CatalogUrl]:
    soup = BeautifulSoup(requests.get(url=url.format()).text.encode("UTF-8"), "lxml")

    majors: Dict[str, CatalogUrl] = {}

    # Make sure there are at least some links
    majorLinks = soup.find("div", {"id": "main"})
    if majorLinks != None:
        for link in majorLinks.findNext("ul").findChildren("li"):
            majors[link.find("a").get_text()] = current_catalog_url.parse_relative_url(
                link.find("a")["href"]
            )

    return majors


"""
`get_classes_from_major` takes in the URL of a specific major, and returns all the
metadata associated with the classes contained within
"""


def get_classes_from_major(url: CatalogUrl) -> List[Tuple[str, Dict[str, CatalogUrl]]]:
    soup = BeautifulSoup(requests.get(url=url.format()).text.encode("UTF-8"), "lxml")

    classes: Dict[str, CatalogUrl] = {}

    # Make sure there are at least some links
    classLinks = soup.find("div", {"id": "main"})
    if classLinks != None:
        for link in classLinks.findNext("ul").findChildren("li"):
            classes[link.find("a").get_text()] = current_catalog_url.parse_relative_url(
                link.find("a")["href"]
            )

    return classes


"""
`get_data_from_class` takes in the URL for a class and returns any metadata needed
from its page

Currently, this only includes the course's description
"""


def get_data_from_class(url: CatalogUrl) -> Dict[str, str]:
    soup = BeautifulSoup(requests.get(url=url.format()).text.encode("UTF-8"), "lxml")

    metadata: Dict[str, str] = {}

    metadata["description"] = soup.find("div", {"class": "desc"}).get_text().strip()

    return metadata


course_catalog = {}

for major_url in tqdm(get_majors_from_homepage(current_catalog_url).values()):
    for fullClassName, classURL in tqdm(
        get_classes_from_major(major_url).items(), leave=False
    ):
        metadata = get_data_from_class(classURL)

        # fullClassName is a string that looks like:
        # Ex: "UBW 100 Intruduction to Basketweaving"
        courseMajor, courseCode, *courseName = fullClassName.split(" ")

        metadata["subj"] = courseMajor
        # Try to convert the course number into an int (ex: 101)
        try:
            metadata["crse"] = int(courseCode)
        except ValueError:  # Courses with non-letter grades (ex: 101L)
            metadata["crse"] = courseCode
        # This leaves courseName as a list of all the other words in the course's
        # name, so we want to put them all together
        metadata["name"] = " ".join(courseName)

        course_catalog[f"{courseMajor}-{courseCode}"] = metadata

# Write course catalog to disk
with open(f"catalog.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(course_catalog, outfile, sort_keys=True, indent=2)
