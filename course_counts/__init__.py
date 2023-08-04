import urllib3
import requests
import logging

from bs4 import BeautifulSoup

from typing import Self

logging.basicConfig(level=logging.INFO)


class CourseCountsContext:
    view_state: str
    view_state_generator: str
    view_state_encrypted: str
    event_validation: str

    def __init__(
        self,
        view_state: str,
        view_state_generator: str,
        view_state_encrypted: str,
        event_validation: str,
    ):
        self.view_state = view_state
        self.view_state_generator = view_state_generator
        self.view_state_encrypted = view_state_encrypted
        self.event_validation = event_validation

    def parse(source: BeautifulSoup) -> Self:
        return CourseCountsContext(
            view_state=source.find(id="__VIEWSTATE")["value"],
            view_state_generator=source.find(id="__VIEWSTATEENCRYPTED")["value"],
            view_state_encrypted=source.find(id="__VIEWSTATEENCRYPTED")["value"],
            event_validation=source.find(id="__EVENTVALIDATION")["value"],
        )


COURSE_COUNTS_HOMEPAGE = "https://counts.oxy.edu/public/default.aspx"

COURSE_COUNTS_REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}

COURSE_COUNTS_CACHE_FILE = "cached_response.html"


# Ignore the SSL errors, because course counts has some errors with it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


from .counts import *
