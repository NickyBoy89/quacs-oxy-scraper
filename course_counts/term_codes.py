from __future__ import annotations

from enum import Enum


class TermCode(Enum):
    Fall = 1
    Spring = 2
    Summer = 3

    def from_semester_code(code: str) -> TermCode:
        # Match on the last two characters
        return TermCode(int(code[-2:]))

    # These are all hardcoded by semester date
    def end_date(self) -> str:
        match self:
            case Fall:
                return "11/20"
            case Spring:
                return "4/27"
            case Summer:
                return "8/6"

    def start_date(self) -> str:
        match self:
            case Fall:
                return "8/24"
            case Spring:
                return "1/19"
            case Summer:
                return "5/1"

    # Hardcoded semester start and end dates
    if term[-2:] == "01":  # Fall
        timeslots["dateStart"] = "8/24"
        timeslots["dateEnd"] = "11/20"
    elif term[-2:] == "02":  # Spring
        timeslots["dateStart"] = "1/19"
        timeslots["dateEnd"] = "4/27"
    elif term[-2:] == "03":  # Summer
        timeslots["dateStart"] = "5/1"
        timeslots["dateEnd"] = "8/6"
