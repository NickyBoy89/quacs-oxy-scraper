import json

from bs4 import NavigableString

from typing import List, Dict, Any, Self


class ParsedClassPage:
    restrictions: str
    corequisites: str
    prereqs: str
    reserved: str
    # Not sure what this is used for
    text_key: str

    def __init__(
        self,
        restrictions: str,
        corequisites: str,
        prereqs: str,
        reserved: str,
        text_key: str = "",
    ) -> None:
        self.restrictions = restrictions
        self.corequisites = corequisites
        self.prereqs = prereqs
        self.reserved = reserved
        self.text_key = text_key

    def __repr__(self) -> str:
        return f"ParsedClassPage {{ \
                restrictions: {self.restrictions}, \
                corequisites: {self.corequisites}, \
                prereqs: {self.prereqs}, \
                reserved: {self.reserved}, \
                text_key: {self.text_key}}}"


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

    def __repr__(self) -> str:
        return f"ParsedReservation {{ \
                reserved_for: {self.reserved_for}, \
                max_seats: {self.max_seats}, \
                open_seats: {self.open_seats} }}"


class ParsedRestrictions:
    must_be: List[str]
    may_not_be: List[str]

    def __repr__(self) -> str:
        return f"ParsedRestrictions {{ \
                must_be: {self.must_be}, \
                may_not_be: {self.may_not_be} }}"

    def __dict__(self) -> Dict[str, Any]:
        output: Dict[str, Dict[str, List[str]]] = {"classification": {}}
        if len(self.may_not_be) > 0:
            output["classification"]["may_not_be"] = self.may_not_be
        if len(self.must_be) > 0:
            output["classification"]["must_be"] = self.must_be

        return output

    def __init__(self) -> None:
        self.must_be = []
        self.may_not_be = []

    @staticmethod
    def parse(restriction_list: List[NavigableString]) -> Self:
        restrictions_text = list(map(lambda item: item.text, restriction_list))

        restr = ParsedRestrictions()

        for line in restrictions_text:
            if "students may not enroll in this class" in line:
                restr.may_not_be += extract_classes(line)
            elif "students may enroll in this class" in line:
                restr.must_be += extract_classes(line)

        return restr


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
