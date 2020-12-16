import re

def parse(data):

    # Parse parenthesies and clean up the data
    data = parseParenthesies(data)

    logicOperators = getOperators(data)

    if (isinstance(data[-1], list)):
        result = addOperator(logicOperators[-1][0], addGroupedElements(data))
    else:
        result = addOperator(logicOperators[-1], addGroupedElements(data))

    # print(logicOperators)
    print(result)


    return 0

def addGroupedElements(elements):

    result = []

    logicOperators = getOperators(elements)

    baseOperator = logicOperators[-1]

    for element in enumerate(reversed(elements)):
        if (isinstance(element[1], list)):
            result.append(addOperator(getFirstElement(logicOperators[len(elements) - element[0]]), addGroupedElements(element[1])))
        elif (logicOperators[element[0]] == baseOperator):
            result.append(addCourse(stripOperator(element[1])))
        else:
            result.append(addOperator(logicOperators[len(elements) - element[0]], addGroupedElements(elements[element[0]:])))

    return result

def addCourse(courseName):
    return {
        "type": "course",
        "course": courseName
    }

def stripOperator(term):
    return re.search(""" (.*)""", term.strip()).group(0).strip()

def addOperator(name, courses):

    result = {
        "type": name,
        "nested": []
    }

    for course in courses:
        result["nested"].append(course)

    return result

def getOperators(data):

    logicOperators = []

    carryoverTerm = False

    for term in enumerate(data):
        if (isinstance(term[1], list)):
            logicOperators.append(getOperators(term[1]))
        elif ("and" in term[1]):
            logicOperators.append("and")
            if (carryoverTerm):
                logicOperators[term[0] - 1] = "and"
                carryoverTerm = False
        elif ("or" in term[1]):
            logicOperators.append("or")
            if (carryoverTerm):
                logicOperators[term[0] - 1] = "or"
                carryoverTerm = False
        else:
            logicOperators.append("")
            carryoverTerm = True

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

def groupStatements(data):
    result = []

    for state in enumerate(data):
        pass

def getFirstElement(element):
    if (isinstance(element, list)):
        return getFirstElement(element[0])
    else:
        return element

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
