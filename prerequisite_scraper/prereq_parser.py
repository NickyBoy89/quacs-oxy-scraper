import re

def parse(data):

    # TODO: Parse logic

    # Parse parenthesies and clean up the data
    data = parseParenthesies(data)

    for operator in reversed(getOperators(data)):
        result = addOperator(operator)

    # print(data)

    # print(result)

    return 0

def addCourse(courseName):
    return {
        "type": "course",
        "course": courseName
    }

def addOperator(name, *args):

    result = {
        "type": name,
        "nested": []
    }

    for arg in args:
        result["nested"].append(addCourse(arg))

    return result

def getOperators(data):

    logicOperators = []

    for term in data:
        if (isinstance(term, list)):
            logicOperators.append(getOperators(term))
        elif ("and" in term):
            logicOperators.append("and")
        elif ("or" in term):
            logicOperators.append("or")
        else:
            logicOperators.append("")

    return logicOperators

def getClassRestrictions(text):

    grades = []

    if 'Graduate' in text:
        grades.append('Graduate')
    if 'Senior' in text:
        grades.append('Senior')
    if 'Junior' in text:
        grades.append('Junior')
    if 'Frosh' in text:
        grades.append('Frosh')

    return(grades)

def parseParenthesies(data):

    nestedLevel = 0

    result = [] # Create a list to copy all the data into

    for req in enumerate(data):

        if (nestedLevel > 1):
            raise ValueError("More than one level of parenthesies detected. If this message appears, change the function to add this capability")

        if ("(" in req[1]):
            nestedLevel += 1

            result.append([re.search('\(.+', req[1]).group(0)[1:].strip()])
        elif (")" in req[1]):
            nestedLevel -= 1

            result[-1].append(req[1].strip()[:-1])
        elif (nestedLevel > 0):
            result[-1].append(req[1].strip())
        else:
            result.append(req[1].strip())

    return result
