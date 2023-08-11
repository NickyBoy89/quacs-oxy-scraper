import json

from enum import Enum, unique
from typing import List, Self, Dict, Any


@unique
class Operator(Enum):
    Or = 1
    And = 2

    @staticmethod
    def parse(text: str) -> Self:
        if text == "or":
            return Operator.Or
        elif text == "and":
            return Operator.And
        raise Exception(f'Unknown operator type: "{text}"')

    def __str__(self) -> str:
        return self.name.lower()


class ParsedPrerequisite:
    prefixed_operator: Operator | None = None


class SingleClass(ParsedPrerequisite):
    class_name: str

    def __init__(
        self, class_name: str, prefixed_operator: Operator | None = None
    ) -> None:
        self.class_name = class_name
        self.prefixed_operator = prefixed_operator

    def to_json(self):
        return self.__dict__()

    def __repr__(self) -> str:
        return f"SingleClass {{ prefixed_operator: {self.prefixed_operator}, class_name: {self.class_name} }}"

    def __dict__(self) -> Dict[str, Any]:
        return {"course": self.class_name, "type": "course"}


class ClassGroup(ParsedPrerequisite):
    nested_classes: List[ParsedPrerequisite]

    @staticmethod
    def combine_prereqs(prereqs: List[ParsedPrerequisite]) -> Self:
        current_operator: Operator | None = None
        current_grouping = []

        parsed = ClassGroup()

        for prereq in prereqs:
            if prereq.prefixed_operator == current_operator or current_operator == None:
                current_operator = prereq.prefixed_operator
                current_grouping.append(prereq)
            else:
                new_group = [ClassGroup.combine_prereqs(current_grouping)]
                current_grouping = new_group
                current_operator = prereq.prefixed_operator
                current_grouping.append(prereq)

        parsed.nested_classes = current_grouping
        parsed.prefixed_operator = current_operator

        return parsed

    def __init__(
        self,
        *nested_classes: List[ParsedPrerequisite],
        op: Operator | None = None,
    ):
        self.nested_classes = list(nested_classes)
        self.prefixed_operator = op

    def to_json(self):
        return json.dumps(self.__dict__(), indent=2)

    def __repr__(self) -> str:
        return f"ClassGroup {{ type: {self.prefixed_operator}, nested: {self.nested_classes} }}"

    def __dict__(self) -> Dict[str, Any]:
        # print(type(self.nested_classes))
        # print(self.nested_classes)
        return {
            "nested": list(map(lambda item: item.__dict__(), self.nested_classes)),
            "type": str(self.prefixed_operator),
        }
