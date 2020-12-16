import json

# prerequisites = [['Math 120', 'or Math 124', 'or Math 128', 'or APBC', 'or OXMA'], ['and Phys 120', 'or Phys 125', 'or APPE']]
# prerequisites = ['Math 101', 'and Math 100', 'and Math 201']
prerequisites = ['1', 'and 2', 'and 3', 'or 4']
operators = []

logicOperators = []

for prerequisite in prerequisites:
        if isinstance(prerequisite, list):
            nestedOperators = []
            if 'and' in prerequisite[0]:
                logicOperators.append('and')
            else:
                logicOperators.append('')
            for nested in prerequisite:
                if 'or' in nested:
                    nestedOperators.append('or')
                elif 'and' in nested:
                    nestedOperators.append('and')
                else:
                    nestedOperators.append('')
            operators.append(nestedOperators)
        else:
            if 'or' in prerequisite:
                operators.append('or')
                logicOperators.append('or')
            elif 'and' in prerequisite:
                operators.append('and')
                logicOperators.append('and')
            else:
                operators.append('')
                logicOperators.append('')

if logicOperators[1] == 'and':
    logicOperators[0] = 'and'
elif logicOperators[1] == 'or':
    logicOperators[0] = 'or'

jsonOutput = {}


if logicOperators[-1] == 'and':
    jsonOutput['type'] = 'and'
elif logicOperators[-1] == 'or':
    jsonOutput['type'] = 'or'
jsonOutput['nested'] = []



def getIndexesOfAndGroups(list):
    characterIndexes = [i for i, e in enumerate(list) if e == 'and']
    indexLocations = []
    insideAndGroup = False
    for elementLocation in characterIndexes:
        if list[elementLocation + 1] == 'and':
            insideAndGroup = True
            indexLocations.append(elementLocation)
    return(indexLocations)

tempAddIndex = {'type': 'and', 'nested': []}

for i in characterIndexes:
    if (i+1) in characterIndexes:
        tempAddIndex['nested'].append()
    # if and in logicOperators

# for i in range(len(logicOperators)):
    # jsonOutput['nested'].append({'type': 'course', 'course': prerequisites[i]})


print(operators)
print(logicOperators)
print(json.dumps(jsonOutput))
