import requests, json, re, time, sys
from requests import Session
from bs4 import BeautifulSoup, NavigableString
from tqdm import tqdm
from os import path
import urllib3

from typing import List

from prerequisite_parser import (
    ParsedClassPage,
    ParsedReservation,
    ParsedRestrictions,
    parse_prerequisites,
)

from course_counts import (
    make_individual_class_body,
    fetch_all_courses,
    fetch_landing_page,
    CourseCountsContext,
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
    parsed_class_row: NavigableString,
    session: Session,
    session_context: CourseCountsContext,
) -> List[ParsedClassPage]:
    class_request_body = make_individual_class_body(
        parsed_class_row,
        current_semester,
        ctx,
    )

    # print(class_request_body)

    class_response = session.post(
        url=COURSE_COUNTS_HOMEPAGE,
        data=class_request_body,
        headers=COURSE_COUNTS_REQUEST_HEADER,
    )
    response = BeautifulSoup(class_response.text, "html.parser")

    restrictions: List[str] = []
    corequisites: List[str] = []
    prerequisites: List[str] = []
    reserved: List[str] = []

    restrictions_panel = response.find(id="restrictionsPanel")
    corequisites_panel = response.find(id="corequisitesPanel")
    prereqs_panel = response.find(id="prereqsPanel")
    reserved_panel = response.find(id="resvDetailsPanel")

    # print(restrictions_panel, corequisites_panel, prereqs_panel, reserved_panel)

    if restrictions_panel != None:
        restrictions = ParsedRestrictions.parse(
            restrictions_panel.find("ul").find_all("li")
        )
    if corequisites_panel != None:
        # The corequisite format looks something like this:
        # COMP 131 1-1 (1059), COMP 131 1-2 (1060)
        corequisite_text = corequisites_panel.find("span", id="lblCorequisites").text
        for coreq_course in corequisite_text.split(", "):
            department, course_number, *_ = coreq_course.split(" ")
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


def parse_reserved_seats(
    reserved_seat_rows: List[NavigableString],
) -> List[ParsedReservation]:
    reservations = []

    for row in reserved_seat_rows:
        reservation_name, max_seats, open_seats = row.find_all("td")
        reservations.append(
            ParsedReservation(
                reserved_for=reservation_name.text,
                max_seats=max_seats.text,
                open_seats=open_seats.text,
            )
        )

    return reservations


session = requests.Session()

landing = fetch_landing_page(session=session)
ctx = CourseCountsContext.parse(landing)

all_courses = fetch_all_courses(
    current_semester, ctx, session=session, caching_enabled=True
)

# Finds all classes by rows
class_rows = all_courses.find("table", id="gvResults").find_all("tr", recursive=False)[
    1:
]

ctx = CourseCountsContext.parse_courses(all_courses)

for class_row in tqdm(class_rows):
    print(parse_class_page_data(class_row, session, ctx))


# Saving data into json file
# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"prerequisites.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(dump, outfile, sort_keys=True, indent=2)

print(time.time() - start)
