from __future__ import annotations

import requests, json, re, sys
from tqdm import tqdm

from bs4 import NavigableString

import requests

from typing import List, Dict, Any

# Import the script to create the mod.rs
import sis

from course_counts import (
    fetch_landing_page,
    fetch_subject_list,
    fetch_all_courses,
    CourseCountsContext,
    TermCode,
)

# You can manually specify a semester code for the script to use
if len(sys.argv) > 1:
    current_semester = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        current_semester = semesters.readlines()[-1].strip()

output: List[Dict[str, Any]] = []


for subject in fetch_subject_list():
    output.append({"name": subject.text, "code": subject["value"], "courses": []})

# Maps the course code to the course name (ex: AMST is mapped to American Studies)
codeMapping = {}

catalog_data: Dict[str, Dict[str, Any]] = {}

# Get the course catalog data to get some of the things that we have already generated
with open("catalog.json") as catalog_json:
    catalog_data = json.load(catalog_json)


def time_to_military(time: str, use_start_time: bool) -> int:
    if "TBD" in time:
        return -1
    if use_start_time:
        time = time.split("-")[0]
    else:
        time = time.split("-")[1]

    offset = 0
    if "pm" in time and "12:" not in time:
        offset = 1200
    return int("".join(time.strip().split(":"))[:4]) + offset


def get_class_data_from_row(data: NavigableString) -> CourseDescription:
    (
        crn,
        course_name,
        course_title,
        unit_count,
        instructor,
        meeting_times,
        core_sections,
        max_seats,
        enrolled_seats,
        *_,
    ) = data.find_all("td", recursive=False)

    # The name of the course contains the subject, course code, the section number, and related courses
    # For example: COMP 131 1 means:
    # * COMP is the subject
    # * 131 is the course code
    # * 1 is the section number
    #   * Sections can be zero-indexed if they are the only class of that type
    # For lab classes, this a little more complicated
    # For example: COMP 131 2-2 means:
    # * COMP is the subject
    # * 131 is the course code
    # * 2-2 means:
    #   * The first 2 means it belongs to the second section
    #   * The second 2 means it is the second section of that lab class

    course_subject, course_code, section, *_ = course_name.text.split(" ")

    section_number: int
    lab_related_section: int | None = None

    # If the section number is one digit, then append a zero to the front
    if not "-" in section and len(section) == 1:
        section = "0" + section

    course = CourseDescription()
    course.crn = int(crn.find("a", recursive=False).text)
    course.subj = course_subject
    course.crse = course_code
    course.sec = section
    course.credMin = int(unit_count.text)
    course.credMax = int(unit_count.text)
    course.title = course_title.text
    course.max_seats = int(max_seats.text)
    course.enrolled = int(enrolled_seats.text)

    # Leave the attribute blank
    course.attribute = ""

    # Start parsing the timeslots
    timeslots = Timeslot()

    # If there is a professor specified (not TBD)
    if instructor.find("abbr") != None:
        timeslots.instructor = instructor.find("abbr")["title"]

    # Parse the timeslot table
    timeslot_table = meeting_times.find("table")
    course_times, course_days, *_ = timeslot_table.find_all("td")

    # If the days is TBD, keep it as an empty list
    if course_days.text != "Days-TBD":
        timeslots.start_time = time_to_military(course_times.text, use_start_time=True)
        timeslots.end_time = time_to_military(course_times.text, use_start_time=False)

        timeslots.days = list(course_days.text)

    # Hardcoded semester start and end dates
    current_term = TermCode.from_semester_code(current_semester)
    timeslots.start_date = current_term.start_date()
    timeslots.end_date = current_term.end_date()

    course.timeslots = [timeslots]

    return course


class Timeslot:
    days: List[str] = []
    instructor: str = "Instructor-TBD"
    start_time: int | None = None
    end_time: int | None = None
    start_date: str
    end_date: str

    def to_json(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "days": self.days,
            "instructor": self.instructor,
            "location": "",
        }

        if self.days != []:
            result["timeStart"] = self.start_time
            result["timeEnd"] = self.end_time

        result["dateStart"] = self.start_date
        result["dateEnd"] = self.end_date

        return result


class CourseDescription:
    crn: int
    # Course subject, ex: COMP
    subj: str
    # Course number, ex: 131 or 131L
    crse: str
    sec: str
    credMin: int
    credMax: int
    title: str
    # Capacity of the course
    max_seats: int
    # Seats accounted for
    enrolled: int
    attribute: str
    timeslots: List[Timeslot]

    def generate_header(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "subj": self.subj,
            "crse": self.crse,
            "id": f"{self.subj}-{self.crse}",
            "sections": [self.to_json()],
        }

    def to_json(self) -> Dict[str, Any]:
        return {
            "crn": self.crn,
            "subj": self.subj,
            "crse": self.crse,
            "sec": self.sec,
            "credMin": self.credMin,
            "credMax": self.credMax,
            "title": self.title,
            "cap": self.max_seats,
            "act": self.enrolled,
            "rem": self.max_seats - self.enrolled,
            "attribute": self.attribute,
            "timeslots": list(map(lambda item: item.to_json(), self.timeslots)),
        }


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

for row in tqdm(class_rows):
    course_description = get_class_data_from_row(row)
    for department in output:
        if department["code"] == course_description.subj:
            # There are two cases:
            # * The course is already here, in which case the new course is added
            #   to the list of sections
            # * Or, a new header is generated for the course, and the course is added

            existing_course_codes = list(
                map(lambda course: course["crse"], department["courses"])
            )

            # If the course already exists, add it to the list of sections
            try:
                existing_course_index = existing_course_codes.index(
                    course_description.crse
                )
                department["courses"][existing_course_index]["sections"].append(
                    course_description.to_json()
                )
            except ValueError:  # The course does not already exist
                department["courses"].append(course_description.generate_header())

# Generate the mod.rs file from the data
print("Generating mod.rs")
sis.genmod(output, None)
print("Done generating mod.rs")

# Saving data into json file
# print(json.dumps(dump, indent=4, sort_keys=True))
with open(f"courses.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(output, outfile, sort_keys=False, indent=2)
