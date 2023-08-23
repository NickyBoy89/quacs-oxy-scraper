import re, json
import logging

from typing import List, Dict, Tuple

from .prerequisites import ParsedPrerequisite, SingleClass, ClassGroup, Operator


def parse_prerequisite_list(prereq_list: List[str]) -> ParsedPrerequisite:
    assert type(prereq_list) == list
    return parse_prerequisites("\n".join(prereq_list))


def parse_prerequisites(text: str) -> ParsedPrerequisite:
    assert type(text) == str
    start_index = 0

    parsed: List[ParsedPrerequisite] = []

    index = 0
    while index < len(text):
        match text[index]:
            case "(":
                end = index_matching_parentheses(text, index)
                text_block = text[index + 1 : end]
                # print(f"Parsing the contents of: {text_block}")
                result = parse_prerequisites(text_block)
                # print(f"Received the resulting object: {result}")
                parsed.append(result)
                index = end + 1
                start_index = index
            case "\n":
                parsed.append(parse_single_course(text[start_index : index + 1]))
                start_index = index
            # Handle the case where the list ends
            case _ if index == len(text) - 1:
                parsed.append(parse_single_course(text[start_index : index + 1]))
        index += 1

    # Mark the first element as the start of the group
    parsed[0].is_leading = True

    if len(parsed) > 1:
        return ClassGroup.combine_prereqs(parsed)
    return parsed[0]


"""
`index_matching_parenthesies` returns the index of the matching parenthesies, in the
supplied string `text` at the supplied offset `text`
"""


def index_matching_parentheses(text: str, start_index: int) -> int:
    index = start_index

    paren_balance = 0
    while index < len(text):
        match text[index]:
            case "(":
                paren_balance += 1
            case ")":
                paren_balance -= 1
                if paren_balance == 0:
                    return index
        index += 1

    logging.warn("Could not find matching parethesies while parsing prerequisites")
    return start_index


def parse_single_course(text: str) -> SingleClass:
    words = text.strip("()\n").split(" ")
    # Remove empty strings
    words = list(filter(lambda item: item != "", words))

    # print(f"Parsing [{words}]")

    operator: Operator | None = None
    match words:
        case ["or", *rest]:
            return SingleClass(prefixed_operator=Operator.Or, class_name=" ".join(rest))
        case ["and", *rest]:
            return SingleClass(
                prefixed_operator=Operator.And, class_name=" ".join(rest)
            )

    return SingleClass(class_name=" ".join(words))
