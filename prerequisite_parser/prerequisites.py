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
    is_leading: bool = False


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
        return f"SingleClass {{ prefixed_operator: {self.prefixed_operator}, class_name: {self.class_name}, leading: {self.is_leading} }}"

    def __dict__(self) -> Dict[str, Any]:
        return {"course": self.class_name, "type": "course"}


class ClassGroup(ParsedPrerequisite):
    nested_classes: List[ParsedPrerequisite]
    group_type: Operator

    @staticmethod
    def combine_prereqs(prereqs: List[ParsedPrerequisite]) -> Self:
        current_grouping = []

        parsed = ClassGroup(op=Operator.Or)

        for prereq in prereqs:
            if len(current_grouping) > 0:
                match prereq.prefixed_operator:
                    # `and` prefixed classes get added to the current group
                    case Operator.And:
                        pass
                    # `or` operators flush the current group and get added to
                    # the parsed output
                    case Operator.Or:
                        # TODO: Test what's already on the stack, if there is an `or`
                        if len(current_grouping) > 0:
                            most_recent = current_grouping[-1]
                            # If there is an `and` in the current group, flush it
                            if (
                                most_recent.prefixed_operator == Operator.And
                                and not most_recent.is_leading
                            ):
                                parsed.nested_classes.append(
                                    ClassGroup.combine_prereqs(current_grouping)
                                )
                            # Otherwise, add it to the parsed output
                            else:
                                assert len(current_grouping) == 1
                                parsed.nested_classes.append(most_recent)

                            # Whatever the case, flush the current group
                            current_grouping = []

            current_grouping.append(prereq)

        # At the end of the iteration, there are two cases:
        # * The list contains one or more `and` grouped elements, which we have
        #   to combine and add to the list of parsed classes
        # * The list contains an `or` element, where we add it to the list of
        #   parsed classes

        # We also should never have an empty list
        assert len(current_grouping) != 0

        match current_grouping[-1].prefixed_operator:
            case Operator.And:
                # If there are no other parsed elements, this is a purely an `and` group,
                # which we need to update directly
                #
                # Otherwise, we add a new element to the end
                result = ClassGroup(op=Operator.And)
                result.nested_classes = current_grouping

                if len(parsed.nested_classes) > 0:
                    parsed.nested_classes.append(result)
                else:
                    parsed = result
            case Operator.Or:
                # There should only ever be one `or` statement at a time
                assert len(current_grouping) == 1

                parsed.nested_classes.append(current_grouping[-1])

        return parsed

    """
    `prefixed_operator` represents the leading operator for a group, which is
    different from the group's type

    The operator differs in the fact that it represents what operator the group 
    has been prefixed with
    """

    @property
    def prefixed_operator(self) -> Operator | None:
        if len(self.nested_classes) == 0:
            return None

        assert len(self.nested_classes) > 1

        first_element = self.nested_classes[0]
        if type(first_element) == ClassGroup:
            return first_element.prefixed_operator
        return first_element.prefixed_operator

    def __init__(
        self,
        *nested_classes: List[ParsedPrerequisite],
        op: Operator | None = None,
    ) -> None:
        self.nested_classes = list(nested_classes)
        self.group_type = op

    def to_json(self):
        return json.dumps(self.__dict__(), indent=2)

    def __repr__(self) -> str:
        return (
            f"ClassGroup {{ type: {self.group_type}, nested: {self.nested_classes} }}"
        )

    def __dict__(self) -> Dict[str, Any]:
        return {
            "nested": list(map(lambda item: item.__dict__(), self.nested_classes)),
            "type": str(self.group_type),
        }
