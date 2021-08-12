import requests, json, re, time, sys
from bs4 import BeautifulSoup
from tqdm import tqdm
from os import path
import urllib3

# Import counts
sys.path.insert(1, ".")
from counts import counts

with open("semesters.json", "w") as schools:
    # Write the semesters to the file
    for semester in counts.semesters():
        schools.write(semester["value"] + "\n")
        # Stop when you get to the currently selected one
        if semester.has_attr("selected"):
            break
