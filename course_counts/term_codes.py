from __future__ import annotations

from enum import Enum


class TermCode(Enum):
    Fall = 1
    Spring = 2
    Summer = 3

    @staticmethod
    def from_semester_code(code: str) -> TermCode:
        # Match on the last two characters
        return TermCode(int(code[-2:]))

    def end_date(self) -> str:
        match self:
            case TermCode.Fall:
                return "11/20"
            case TermCode.Spring:
                return "4/27"
            case TermCode.Summer:
                return "8/6"

    def start_date(self) -> str:
        match self:
            case TermCode.Fall:
                return "8/24"
            case TermCode.Spring:
                return "1/19"
            case TermCode.Summer:
                return "5/1"
