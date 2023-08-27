from __future__ import annotations

import urllib3
import requests
import logging

import re

from bs4 import BeautifulSoup

from typing import Self

logging.basicConfig(level=logging.INFO)


class CourseCountsContext:
    # Context
    client_state: str

    # State variables
    view_state: str
    view_state_generator: str
    view_state_encrypted: str
    event_validation: str

    def __init__(
        self,
        client_state: str,
        view_state: str,
        view_state_generator: str,
        view_state_encrypted: str,
        event_validation: str,
    ):
        self.client_state = client_state
        self.view_state = view_state
        self.view_state_generator = view_state_generator
        self.view_state_encrypted = view_state_encrypted
        self.event_validation = event_validation

    def parse(source: BeautifulSoup) -> CourseCountsContext:
        return CourseCountsContext(
            client_state=source.find(id="tabContainer_ClientState")["value"],
            view_state=source.find(id="__VIEWSTATE")["value"],
            view_state_generator=source.find(id="__VIEWSTATEENCRYPTED")["value"],
            view_state_encrypted=source.find(id="__VIEWSTATEENCRYPTED")["value"],
            event_validation=source.find(id="__EVENTVALIDATION")["value"],
        )

    def parse_courses(source: BeautifulSoup) -> CourseCountsContext:
        # These values are embedded in the source of the page, so they need to
        # be extracted
        return CourseCountsContext(
            view_state=re.findall("(?<=(\|__VIEWSTATE\|))(.*?)(?=\|)", source.text)[0][
                1
            ],
            view_state_generator=re.findall(
                "(?<=(\|__VIEWSTATEGENERATOR\|))(.*?)(?=\|)", source.text
            )[0][1],
            event_validation=re.findall(
                "(?<=(\|__EVENTVALIDATION\|))(.*?)(?=\|)", source.text
            )[0][1],
            client_state="""{"ActiveTabIndex":0,"TabEnabledState":[true,true,true,true,true],"TabWasLoadedOnceState":[true,false,false,false,false]}""",
            view_state_encrypted=re.findall(
                "(?<=(\|__VIEWSTATEENCRYPTED\|\|))(.*?)(?=\|)", source.text
            )[0][1],
        )


COURSE_COUNTS_HOMEPAGE = "https://counts.oxy.edu/public/default.aspx"

COURSE_COUNTS_REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}

COURSE_COUNTS_CACHE_FILE = "cached_response.html"


# Ignore the SSL errors, because course counts has some errors with it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


from .counts import *
from .counts_requests import *
from .term_codes import TermCode
