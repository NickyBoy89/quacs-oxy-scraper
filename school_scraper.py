import json, sys
from tqdm import tqdm

from typing import List, Dict, Any, Tuple

from enum import Enum, unique

from course_catalog import CatalogUrl, get_majors_from_homepage


@unique
class MajorGroup(Enum):
    ForeignLang = "Foreign Languages and Studies"
    Humanities = "Humanities, Arts, and Social Sciences"
    Politics = "Politics and Public Relations"
    Social = "Social Affairs"
    Sciences = "Sciences"
    Literature = "Literature"


# Some default custom groupings that I thought were fitting to reduce the number of elements on the main page
school_groupings = {
    # Foreign Language
    "Arabic": MajorGroup.ForeignLang,
    "French": MajorGroup.ForeignLang,
    "German": MajorGroup.ForeignLang,
    "Greek": MajorGroup.ForeignLang,
    "Russian": MajorGroup.ForeignLang,
    "Japanese Studies": MajorGroup.ForeignLang,
    "Spanish": MajorGroup.ForeignLang,
    "Latin": MajorGroup.ForeignLang,
    "Latino/a and Latin American Studies": MajorGroup.ForeignLang,
    "East Asian Studies": MajorGroup.ForeignLang,
    "Chinese Studies": MajorGroup.ForeignLang,
    # Humanities
    "Studio Art": MajorGroup.Humanities,
    "Art History": MajorGroup.Humanities,
    "Media Arts and Culture": MajorGroup.Humanities,
    "Theater": MajorGroup.Humanities,
    "Music": MajorGroup.Humanities,
    "Music Applied Study": MajorGroup.Humanities,
    "Comparative Studies in Literature and Culture": MajorGroup.Humanities,
    "Economics": MajorGroup.Humanities,
    "History": MajorGroup.Humanities,
    "Philosophy": MajorGroup.Humanities,
    "Sociology": MajorGroup.Humanities,
    "Education": MajorGroup.Humanities,
    "Religious Studies": MajorGroup.Humanities,
    "Linguistics": MajorGroup.Humanities,
    # Political Science
    "Diplomacy & World Affairs": MajorGroup.Politics,
    "Politics": MajorGroup.Politics,
    # Social Affairs
    "Urban & Environmental Policy": MajorGroup.Social,
    "Public Health": MajorGroup.Social,
    "Critical Theory and Social Justice": MajorGroup.Social,
    # Sciences
    "Biochemistry": MajorGroup.Sciences,
    "Biology": MajorGroup.Sciences,
    "Chemistry": MajorGroup.Sciences,
    "Geology": MajorGroup.Sciences,
    "Cognitive Science": MajorGroup.Sciences,
    "Mathematics": MajorGroup.Sciences,
    "Physics": MajorGroup.Sciences,
    "Psychology": MajorGroup.Sciences,
    "Computer Science": MajorGroup.Sciences,
    "Kinesiology": MajorGroup.Sciences,
    # Literature
    "English": MajorGroup.Literature,
    "Writing & Rhetoric": MajorGroup.Literature,
}

if len(sys.argv) > 1:
    term = sys.argv[1]
else:
    with open("semesters.json") as semesters:
        # Get the last semester number, but remove the newline
        term = semesters.read().split("\n")[-2]

current_catalog_url = CatalogUrl()
current_catalog_url.language = "en"
current_catalog_url.root_url = "https://oxy.smartcatalogiq.com"

# Get the academic year based on the term code
# This is in the format of `202301`, where the first three characters are the year
# and the rest are the semester code
assert len(term) == 6

current_catalog_url.current_year = int(term[:4])

"""
`parse_major_name` takes in a string representing the name of the major, and 
returns a tuple containing the acronym for the major and its full name

For example, this could be something such as:
    `WRD - Writing & Rhetoric` -> Tuple["WRD", "Writing & Rhetoric"]
"""


def parse_major_name(raw_name: str) -> Tuple[str, str]:
    short_name, full_name, *_ = raw_name.split("-")
    return (short_name.strip(), full_name.strip())


# Fetch the list of majors from the front of the catalog page
# This will result in a dictionary of mappings of type Dict[str, CatalogUrl]
# Where `str` is something such as `WRD - Writing & Rhetoric`
majors = get_majors_from_homepage(current_catalog_url)

"""
`groups` represents a list of group entries

Each group entry is formatted as:
{
    "name": "Foreign Language and Studies",
    "depts": [
        {
            "code": "ARAB",
            "name": "Arabic"
        }
    ]
}
"""
groups: List[Dict[str, Any]] = []

# Add the preliminary groups to the list
for group in MajorGroup:
    groups.append({"name": group.value, "depts": []})

for major_text in majors.keys():
    major_code, major_name = parse_major_name(major_text)

    major_group: str
    # If there is a grouping for that major, place the major in that group
    if major_name in school_groupings:
        major_group = school_groupings[major_name].value
        for group_index, group in enumerate(groups):
            if group["name"] == major_group:
                groups[group_index]["depts"].append(
                    {
                        "code": major_code,
                        "name": major_name,
                    }
                )
    # Otherwise, place that major in a group named their name
    else:
        groups.append(
            {
                "name": major_name,
                "depts": [
                    {
                        "code": major_code,
                        "name": major_name,
                    }
                ],
            }
        )


with open(f"schools.json", "w") as outfile:  # -{os.getenv("CURRENT_TERM")}
    json.dump(groups, outfile, sort_keys=False, indent=2)
