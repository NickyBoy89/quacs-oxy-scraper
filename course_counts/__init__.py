import urllib3
import requests
import logging

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

COURSE_COUNTS_HOMEPAGE = "https://counts.oxy.edu/public/default.aspx"

COURSE_COUNTS_REQUEST_HEADER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
}

COURSE_COUNTS_CACHE_FILE = "cached_response.html"


# Ignore the SSL errors, because course counts has some errors with it
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Request the initial data
session = requests.Session()

logging.info("Loading course counts")
landing_page = session.get(COURSE_COUNTS_HOMEPAGE, verify=False)
parsed_landing_page = BeautifulSoup(landing_page.text, "html.parser")
