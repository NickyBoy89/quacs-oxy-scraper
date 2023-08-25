from __future__ import annotations

from bs4 import NavigableString

from typing import List, Dict, Any, Self

from .prerequisites import ParsedPrerequisite


class ParsedRestrictions:
    must_be: List[str]
    may_not_be: List[str]

    def __repr__(self) -> str:
        return f"ParsedRestrictions {{ \
must_be: {self.must_be}, \
may_not_be: {self.may_not_be} }}"

    def to_json(self) -> Dict[str, Any]:
        output: Dict[str, Dict[str, List[str]]] = {"classification": {}}
        if len(self.may_not_be) > 0:
            output["classification"]["may_not_be"] = self.may_not_be
        if len(self.must_be) > 0:
            output["classification"]["must_be"] = self.must_be

        return output

    def is_empty(self) -> bool:
        return len(self.must_be) == 0 and len(self.may_not_be) == 0

    def __init__(self) -> None:
        self.must_be = []
        self.may_not_be = []

    @staticmethod
    def parse(restriction_list: List[NavigableString]) -> ParsedRestrictions:
        restrictions_text = list(map(lambda item: item.text, restriction_list))

        restr = ParsedRestrictions()

        for line in restrictions_text:
            if "students may not enroll in this class" in line:
                restr.may_not_be += extract_classes(line)
            elif "students may enroll in this class" in line:
                restr.must_be += extract_classes(line)

        return restr


class ParsedClassPage:
    restrictions: ParsedRestrictions
    corequisites: List[str]
    prereqs: ParsedPrerequisite
    reserved: List[ParsedReservation]
    course_crn: int

    def __init__(
        self,
        restrictions: ParsedRestrictions,
        corequisites: List[str],
        prereqs: ParsedPrerequisite,
        reserved: List[ParsedReservation],
        course_crn: int,
    ) -> None:
        self.restrictions = restrictions
        self.corequisites = corequisites
        self.prereqs = prereqs
        self.reserved = reserved
        self.course_crn = course_crn

    def to_json(self) -> Dict[str, Any]:
        result: Dict["str", Any] = {}
        if self.prereqs != None:
            result["prerequisites"] = self.prereqs.to_json()
        if len(self.reserved) > 0:
            result["reserved"] = list(map(lambda item: item.to_json(), self.reserved))
        if len(self.corequisites) > 0:
            result["corequisites"] = self.corequisites
        if self.restrictions != None and not self.restrictions.is_empty():
            result["restrictions"] = self.restrictions.to_json()

        return {str(self.course_crn): result}

    def __repr__(self) -> str:
        return f"ParsedClassPage {{ \
restrictions: {self.restrictions}, \
corequisites: {self.corequisites}, \
prereqs: {self.prereqs}, \
reserved: {self.reserved}, \
course_crn: {self.course_crn}}}"


class ParsedReservation:
    reserved_for: str
    max_seats: int
    open_seats: int

    def __init__(
        self,
        reserved_for: str,
        max_seats: int,
        open_seats: int,
    ) -> None:
        self.reserved_for = reserved_for
        self.max_seats = max_seats
        self.open_seats = open_seats

    def to_json(self) -> Dict[str, Any]:
        return {
            "max": self.max_seats,
            "open": self.open_seats,
            "reservedFor": self.reserved_for,
        }

    def __repr__(self) -> str:
        return f"ParsedReservation {{ \
reserved_for: {self.reserved_for}, \
max_seats: {self.max_seats}, \
open_seats: {self.open_seats} }}"


def extract_classes(input: str) -> List[str]:
    levels = []
    if "Graduate" in input:
        levels.append("Graduate")
    if "Senior" in input:
        levels.append("Senior")
    if "Junior" in input:
        levels.append("Junior")
    if "Frosh" in input:
        levels.append("Frosh")
    return levels
