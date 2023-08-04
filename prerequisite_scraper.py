import requests, json, re, time, sys
from requests import Session
from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm
from os import path
import urllib3

from typing import List

from prerequisite_parser import ParsedClassPage, ParsedReservation, parse_prerequisites

from course_counts import (
    make_class_body,
    fetch_all_courses,
    fetch_landing_page,
    COURSE_COUNTS_HOMEPAGE,
    COURSE_COUNTS_REQUEST_HEADER,
)

import concurrent.futures

current_semester = ""
if len(sys.argv) > 1:
    current_semester = sys.argv[1]
else:
    with open("semesters.json") as semester_data:
        current_semester = semester_data.readlines()[-1].strip()


def parse_class_page_data(
    parsed_class_row: NavigableString, session: Session
) -> List[ParsedClassPage]:
    class_request_body = make_class_body(
        parsed_class_row,
        current_semester,
    )

    response = session.post(
        url=COURSE_COUNTS_HOMEPAGE,
        data=class_request_body,
        headers=COURSE_COUNTS_REQUEST_HEADER,
    )

    restrictions: List[str] = []
    corequisites: List[str] = []
    prerequisites: List[str] = []
    reserved: List[str] = []

    restrictions_panel = response.find(id="restrictionsPanel")
    corequisites_panel = response.find(id="corequisitesPanel")
    prereqs_panel = response.find(id="prereqsPanel")
    reserved_panel = response.find(id="resvDetailsPanel")

    if restrictions_panel != None:
        restrictions = restrictions_panel.find("ul").find_all("li")
    if corequisites_panel != None:
        # The corequisite format looks something like this:
        # COMP 131 1-1 (1059), COMP 131 1-2 (1060)
        corequisite_text = corequisites_panel.find("span", id="lblCorequisites")
        for coreq_course in corequisite_text.split(", "):
            department, course_number, _ = coreq_course.split(" ")
            # Note: This can have duplicate courses
            corequisites.append(f"{department}-{course_number}")
    if prereqs_panel != None:
        prereq_rows = prereqs_panel.find_all("tr")[1:]
        rows_text = list(map(lambda row: row.find("td").text, prereq_rows))
        combined_rows = "\n".join(rows_text)

        prerequisites = parse_prerequisites(combined_rows)
    if reserved_panel != None:
        reserved = parse_reserved_seats(reserved_panel.find_all("tr")[1:])

    return ParsedClassPage(
        restrictions=restrictions,
        corequisites=corequisites,
        prereqs=prerequisites,
        reserved=reserved,
        text_key="",
    )


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


def parse_reserved_seats(
    reserved_seat_rows: List[NavigableString],
) -> List[ParsedReservation]:
    reservations = []

    for row in reserved_seat_rows:
        reservation_name, max_seats, open_seats, _ = row.find_all("td")
        reservations.append(
            ParsedReservation(
                reserved_for=reservation_name.text,
                max_seats=max_seats.text,
                open_seats=open_seats.text,
            )
        )

    return reservations


session = requests.Session()

# Finds all classes by rows
class_rows = (
    fetch_all_courses(current_semester, session=session, caching_enabled=True)
    .find("table", id="gvResults")
    .find_all("tr")
)

for class_row in tqdm(class_rows):
    print(parse_class_page_data(class_row, session=session))


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
