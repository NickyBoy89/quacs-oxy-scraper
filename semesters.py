from bs4 import BeautifulSoup

from course_counts.counts import fetch_semester_list

with open("semesters.json", "w") as semester_data:
    for semester in fetch_semester_list():
        semester_data.write(semester["value"] + "\n")
        # Stop when you get to the currently selected one
        if semester.has_attr("selected"):
            break
