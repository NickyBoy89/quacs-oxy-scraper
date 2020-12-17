import re, json

def parse(data):

    # Parse parenthesies and clean up the data
    data = parseParenthesies(data)

    # print(data)
    # print(getOperators(data))

    print(json.dumps(addGroupedElements(data)))

    return addGroupedElements(data)

# Returns already formed JSON
def addGroupedElements(elements):

    print(elements)

    lockedOperator = None

    logicOperators = getOperators(elements)

    baseOperator = logicOperators[-1]

    result = addOperator(baseOperator)

    for element in enumerate(reversed(elements)):
        normIndex = (len(elements) - 1) - element[0]

        if (isinstance(element[1], list)):
            result.append(addGroupedElements(element[1]))
        elif (logicOperators[normIndex] == baseOperator):
            result["nested"].insert(0, addCourse(stripOperator(element[1])))
        else:
            if (logicOperators[normIndex] == lockedOperator):
                continue

            lockedOperator = logicOperators[normIndex]

            lockedOperator = logicOperators[normIndex]
            result["nested"].append(addGroupedElements(elements[:normIndex + 1]))

    return result

def addCourse(courseName):
    return {
        "type": "course",
        "course": courseName
    }

def stripOperator(term):
    if ("and" in term or "or" in term):
        return re.search(""" (.*)""", term.strip()).group(0).strip()
    else:
        return term

def addOperator(name, courses = None):

    result = {
        "type": name,
        "nested": []
    }

    if courses != None:
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
