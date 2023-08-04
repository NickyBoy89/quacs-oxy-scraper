from enum import Enum, unique

from typing import List, Dict, Any


class ParsedClassPage:
    restrictions: str
    corequisites: str
    prereqs: str
    reserved: str
    # Not sure what this is used for
    text_key: str


class ParsedReservation:
    reserved_for: str
    max_seats: int
    open_seats: int


@unique
class Operator(Enum):
    Or = 1
    And = 2

    def parse(text: str):
        if text == "or":
            return Or
        elif text == "and":
            return And
        raise Exception(f'Unknown prerequisite type: "{text}"')

    def __str__(self) -> str:
        return self.name.lower()


class Prerequisite:
    prefixed_operator: Operator | None = None


class SingleClass(Prerequisite):
    class_name: str

    def __dict__(self) -> Dict[Any, Any]:
        return {"course": self.class_name, "type": "course"}


class ClassGroup(Prerequisite):
    nested_classes: List[Prerequisite]

    def __dict__(self) -> Dict[Any, Any]:
        return {"nested": self.nested_classes, "type": self.prefixed_operator}
