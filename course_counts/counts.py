import urllib3, requests
from os import path
from bs4 import BeautifulSoup, Tag, NavigableString
from requests import Session

from . import (
    COURSE_COUNTS_HOMEPAGE,
    COURSE_COUNTS_REQUEST_HEADER,
    COURSE_COUNTS_CACHE_FILE,
    CourseCountsContext,
)


import logging

from typing import List, Dict


def fetch_landing_page(session=requests.Session()) -> BeautifulSoup:
    landing_page = session.get(COURSE_COUNTS_HOMEPAGE, verify=False)
    return BeautifulSoup(landing_page.text, "html.parser")


def fetch_semester_list() -> List[Tag | NavigableString | None]:
    return parsed_landing_page.find(id="tabContainer_TabPanel1_ddlSemesters").find_all(
        "option"
    )


def fetch_subject_list() -> List[Tag | NavigableString | None]:
    return parsed_landing_page.find(id="tabContainer_TabPanel3_ddlAdvSubj").find_all(
        "option"
    )


def extract_context(body: BeautifulSoup) -> CourseCountsContext:
    return CourseCountsContext(
        view_state=body.find(id="__VIEWSTATE")["value"],
        view_state_generator=body.find(id="__VIEWSTATEENCRYPTED")["value"],
        view_state_encrypted=body.find(id="__VIEWSTATEENCRYPTED")["value"],
        event_validation=body.find(id="__EVENTVALIDATION")["value"],
    )


def fetch_all_courses(
    semester_number: str,
    context: CourseCountsContext,
    session=requests.Session(),
    caching_enabled=False,
) -> BeautifulSoup:
    request_body = make_request_body(semester_number, context)

    parsed_courses: BeautifulSoup

    if caching_enabled and path.exists(COURSE_COUNTS_CACHE_FILE):
        logging.warning("Using cached response data, may be out-of-date")
        with open(COURSE_COUNTS_CACHE_FILE) as cached_data:
            parsed_courses = BeautifulSoup(cached_data.read(), "html.parser")
    else:
        logging.info("Requesting all classes from server, this may take a bit")
        response = session.post(
            COURSE_COUNTS_HOMEPAGE,
            data=request_body,
            headers=COURSE_COUNTS_REQUEST_HEADER,
            verify=False,
        )

        if caching_enabled:
            logging.warning(
                f"Since caching is enabled, a copy of the response is being saved to {COURSE_COUNTS_CACHE_FILE} for future runs"
            )
            with open(COURSE_COUNTS_CACHE_FILE, "w") as cache_file:
                cache_file.write(response.text)

        parsed_courses = BeautifulSoup(response.text, "html.parser")

    return parsed_courses
