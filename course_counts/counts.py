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


def make_request_body(
    selected_semester: str,
    context: CourseCountsContext,
) -> Dict[str, str]:
    return {
        "ScriptManager2": """pageUpdatePanel|tabContainer$TabPanel1$btnGo""",
        "tabContainer_ClientState": parsed_context.find(id="tabContainer_ClientState")[
            "value"
        ],
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": context.view_state,
        "__VIEWSTATEGENERATOR": context.view_state_generator,
        "__VIEWSTATEENCRYPTED": context.view_state_encrypted,
        "__EVENTVALIDATION": context.event_validation,
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
        "tabContainer$TabPanel5$ddlCatalogYear": "200801",
        "__ASYNCPOST": "true",
        "tabContainer$TabPanel1$btnGo": "Go",
    }


def make_class_body(
    parsed_class_row: NavigableString,
    current_semester: str,
    context: CourseCountsContext,
):
    # The first column contains the link to the course page
    # The link looks something like: javascript:__doPostBack('gvResults$ctl02$lnkBtnCrn','')
    strip_prefix = "javascript:__doPostBack('"
    strip_suffix = "', '')"

    class_button = (
        data.find("td")
        .find("a")["href"]
        .removeprefix(strip_prefix)
        .removesuffix(strip_suffix)
    )

    return {
        "ScriptManager2": f"searchResultsPanel|{class_button}",
        "tabContainer$TabPanel1$ddlSemesters": current_semester,
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
        "tabContainer$TabPanel5$ddlCatalogYear": "200801",
        "__EVENTTARGET": class_button,
        "__EVENTARGUMENT": "",
        "__LASTFOCUS": "",
        "__VIEWSTATE": context.view_state,
        "__VIEWSTATEGENERATOR": context.view_state_generator,
        "__VIEWSTATEENCRYPTED": context.view_state_encrypted,
        "__EVENTVALIDATION": context.event_validation,
        "tabContainer_ClientState": """{"ActiveTabIndex":0,"TabEnabledState":[true,true,true,true,true],"TabWasLoadedOnceState":[true,false,false,false,false]}""",
        "__ASYNCPOST": "true",
    }
