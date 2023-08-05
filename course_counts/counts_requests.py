from . import CourseCountsContext

from bs4 import NavigableString
from typing import Dict


def make_all_courses_request_body(
    selected_semester: str,
    context: CourseCountsContext,
) -> Dict[str, str]:
    return {
        "ScriptManager2": """pageUpdatePanel|tabContainer$TabPanel1$btnGo""",
        "tabContainer_ClientState": context.client_state,
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


def make_individual_class_body(
    parsed_class_row: NavigableString,
    current_semester: str,
    context: CourseCountsContext,
):
    # The first column contains the link to the course page
    # The link looks something like: javascript:__doPostBack('gvResults$ctl02$lnkBtnCrn','')
    strip_prefix = "javascript:__doPostBack('"
    strip_suffix = "','')"

    class_button = (
        parsed_class_row.find("a")["href"]
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
