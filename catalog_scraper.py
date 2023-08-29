import requests, sys
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

from typing import List, Tuple, Dict, Self

from course_catalog import (
    CatalogUrl,
    get_majors_from_homepage,
    get_classes_from_major,
    get_data_from_class,
)

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
