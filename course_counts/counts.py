import urllib3, requests
from os import path
from bs4 import BeautifulSoup, Tag, NavigableString

from . import (
    parsed_landing_page,
    session,
    COURSE_COUNTS_HOMEPAGE,
    COURSE_COUNTS_REQUEST_HEADER,
    COURSE_COUNTS_CACHE_FILE,
)

import logging

from typing import List, Dict


def fetch_semester_list() -> List[Tag | NavigableString | None]:
    return parsed_landing_page.find(id="tabContainer_TabPanel1_ddlSemesters").find_all(
        "option"
    )


def fetch_subject_list() -> List[Tag | NavigableString | None]:
    return parsed_landing_page.find(id="tabContainer_TabPanel3_ddlAdvSubj").find_all(
        "option"
    )


def fetch_all_courses(semester_number: str, caching_enabled=False) -> BeautifulSoup:
    request_body = make_request_body(semester_number, parsed_landing_page)

    parsed_courses: BeautifulSoup

    if caching_enabled and path.exists(COURSE_COUNTS_CACHE_FILE):
        logging.info("Using cached response data")
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
            logging.warn(
                f"Since caching is enabled, a copy of the response has been saved to {COURSE_COUNTS_CACHE_FILE} for future runs"
            )
            with open(COURSE_COUNTS_CACHE_FILE, "w") as cache_file:
                cache_file.write(response.text)

        parsed_courses = BeautifulSoup(response.text, "html.parser")

    return parsed_courses


def make_request_body(
    selected_semester: str, parsed_context: BeautifulSoup
) -> Dict[str, str]:
    return {
        "ScriptManager2": """pageUpdatePanel|tabContainer$TabPanel1$btnGo""",
        "tabContainer_ClientState": str(
            parsed_context.find(id="tabContainer_ClientState")["value"]
        ),
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": parsed_context.find(id="__VIEWSTATE")["value"],
        "__VIEWSTATEGENERATOR": parsed_context.find(id="__VIEWSTATEGENERATOR")["value"],
        "__VIEWSTATEENCRYPTED": parsed_context.find(id="__VIEWSTATEENCRYPTED")["value"],
        "__EVENTVALIDATION": parsed_context.find(id="__EVENTVALIDATION")["value"],
        "tabContainer$TabPanel1$ddlSemesters": selected_semester,
        "tabContainer$TabPanel1$ddlSubjects": "",
        "tabContainer$TabPanel1$txtCrseNum": "",
        "tabContainer$TabPanel2$ddlCoreTerms": "201601",
        "tabContainer$TabPanel2$ddlCoreAreas": "CPFA",
        "tabContainer$TabPanel2$ddlCoreSubj": "AMST",
        "tabContainer$TabPanel3$ddlAdvTerms": "201601",
        "tabContainer$TabPanel3$ddlAdvSubj": "AMST",
        "tabContainer$TabPanel3$ddlAdvTimes": "07000755",
        "tabContainer$TabPanel3$ddlAdvDays": "u",
        "tabContainer$TabPanel4$ddlCRNTerms": "201601",
        "tabContainer$TabPanel4$txtCRN": "",
        "tabContainer$TabPanel5$ddlMajorsTerm": "201601",
        "tabContainer$TabPanel5$ddlCatalogYear": "201601",
        "__ASYNCPOST": "true",
        "tabContainer$TabPanel1$btnGo": "Go",
    }
