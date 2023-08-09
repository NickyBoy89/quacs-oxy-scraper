import re, json

from typing import List, Dict, Tuple

from parsed_types import ParsedPrerequisite, SingleClass, ClassGroup, Operator


def parse_prerequisite_list(prereq_list: List[str]) -> ParsedPrerequisite:
    return parse_prerequisites("\n".join(prereq_list))


def parse_prerequisites(text: str) -> ParsedPrerequisite:
    start_index = 0

    parsed = []

    index = 0
    while index < len(text):
        match text[index]:
            case "(":
                try:
                    start, end = match_parentheses(text, index)
                    parsed.append(parse_prerequisites(text[start + 1 : end]))
                    index = end + 1
                    start_index = index
                except Exception as e:
                    pass
            case "\n":
                parsed.append(parse_single_course(text[start_index : index + 1]))
                start_index = index
        index += 1

    print(parsed)


def match_parentheses(text: str, start_index: int) -> Tuple[int, int]:
    index = start_index

    paren_balance = 0
    while index < len(text):
        match text[index]:
            case "(":
                paren_balance += 1
            case ")":
                paren_balance -= 1
                if paren_balance == 0:
                    return (start_index, index)
        index += 1

    raise Exception("Could not find a closing parenthesies")


def parse_single_course(text: str) -> SingleClass:
    print(f"Parsing {text}")

    words = text.strip("()\n").split(" ")

    operator: Operator | None = None
    match words[0]:
        case "or":
            pass
        case "and":
            pass

    # Remove empty strings
    words = list(filter(lambda item: item != "", words))
    match len(words):
        case 3:
            return SingleClass(
                prefixed_operator=Operator.parse(words[0]),
                class_name=" ".join(words[1:]),
            )
        case 2:
            return SingleClass(class_name=" ".join(words[1:]))

    raise Exception(
        f"Unknown number of words encountered while parsing class, got {words}"
    )


def parse(data: List[str], verbose=False) -> Dict[str, str]:
    """
    parse takes in a list of the raw prerequisites
    Ex: ['COURSE', 'or COURSE  NUM`, 'or COURSE  NUM']
    And returns a dict representing the entire dependency tree
    """

    # Clean up the data and parse it into a list of lists
    data = parseParenthesies(data)

    return addGroupedElements(data)


# Parses a list of prerequisites in the form:
# ['CLASS', 'or CLASS', 'and CLASS']
def parseParenthesies(prerequisites: List[str]) -> List[str]:
    """
    parseParenthesies takes in a list of prerequisites of the form
    Ex: [' CLASS', 'or CLASS NUM']
    And returns a list of the parsed prereqs
    """
    # The current balance of the parenthesies, negative means open parenthesies
    # and zero means that everything is balanced
    balance = 0

    result = []  # Create a list to copy all the data into

    for prereq in prerequisites:
        # Remove all double spaces from each prerequisite
        prereq = " ".join(list(filter(None, prereq.split())))
        if balance < -1:
            raise Exception("More than one level of parenthesies in prerequisites")
        if "(" in prereq:
            # If there is parenthesies, adjust the balance, and add the element after the parenthesies
            balance -= 1

            result.append(prereq[prereq.index("(") + 1 :])
        elif ")" in prereq:
            balance += 1

            # On closing parenthesies, append it to the last element's list
            result[-1].append(prereq[: prereq.index(")")])
        elif balance < 0:
            # If there is an open parenthesies, add it to the last element's list
            result[-1].append(prereq)
        else:
            result.append(prereq)

    return result


def addGroupedElements(elements: List[str]) -> Dict[str, str]:
    """
    addGroupedElements takes in the list of prerequisites, and outputs everthing
    as a dictionary with the correct arguments

    Ex: ['COURSE', 'or COURSE  NUM'] ->
    {
        "type": "or",
        "nested": [
            {"type": "course", "course": "COURSE"},
            {"type": "course", "course": "COURSE  NUM"}
                ]
    }
    """
    lockedOperator = None

    logicOperators = getOperators(elements)

    baseOperator = getFirstElement(logicOperators[-1])

    result = addOperator(baseOperator)

    for element in enumerate(reversed(elements)):
        normIndex = (len(elements) - 1) - element[0]

        if isinstance(element[1], list):
            # Modified the logic operators on the beginning of lists
            logicOperators[normIndex][0] = logicOperators[normIndex][1]
            element[1][0] = f"{logicOperators[normIndex][1]} " + stripOperator(
                element[1][0]
            )

            result["nested"].insert(0, addGroupedElements(element[1]))

        elif logicOperators[normIndex] == baseOperator:
            result["nested"].insert(
                0, {"type": "course", "course": stripOperator(element[1])}
            )
        else:
            if logicOperators[normIndex] == lockedOperator:
                continue

            lockedOperator = logicOperators[normIndex]

            lockedOperator = logicOperators[normIndex]
            result["nested"].append(addGroupedElements(elements[: normIndex + 1]))

    # If a class has only one prerequisite, it returns the one course directly
    if result["type"] == "":
        return result["nested"][0]

    return result


def stripOperator(term: str) -> str:
    if "and" in term or "or" in term:
        return " ".join(term.split()[1:])
    return term


def addOperator(name, courses=None):
    result = {"type": name, "nested": []}

    if courses != None:
        for course in courses:
            result["nested"].append(course)
    return result


def getOperators(data):
    logicOperators = []

    carryoverTerm = False

    for term in enumerate(data):
        if isinstance(term[1], list):
            logicOperators.append(getOperators(term[1]))
        elif "and" in term[1]:
            logicOperators.append("and")
            if carryoverTerm:
                logicOperators[term[0] - 1] = "and"
                carryoverTerm = False
        elif "or" in term[1]:
            logicOperators.append("or")
            if carryoverTerm:
                logicOperators[term[0] - 1] = "or"
                carryoverTerm = False
        else:
            logicOperators.append("")
            carryoverTerm = True

    return logicOperators


def getClassRestrictions(text):
    grades = []

    if "Graduate" in text:
        grades.append("Graduate")
    if "Senior" in text:
        grades.append("Senior")
    if "Junior" in text:
        grades.append("Junior")
    if "Frosh" in text:
        grades.append("Frosh")

    return grades


def getFirstElement(element):
    if isinstance(element, list):
        return getFirstElement(element[0])
    return element
