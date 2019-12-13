import yaml
from dice import roll


data = ""

def loadTables(s):
    global data
    with open(s, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def formatTable(table):
    formattedTable: dict
    formattedTable = {'die': table['die'], 'results': {}}
    tableResults = table['results']
    for i in tableResults:
        if "-" in str(i):
            x = i.split("-")
            dieCodes = list(range(int(x[0]), int(x[1])+1))
            for j in dieCodes:
                formattedTable['results'][int(j)] = tableResults[i]
        else:
            formattedTable['results'][int(i)] = tableResults[i]
    return formattedTable

def rollOnTable(table, modifier = 0):
    f_table = formatTable(table)
    die = f_table['die']
    resultList = f_table['results']
    dieRoll = roll(die)+modifier
    keyList = list(resultList.keys())
    if dieRoll < min(keyList):
        dieRoll = min(keyList)
    if dieRoll > max(keyList):
        dieRoll = max(keyList)
    rolledResult = resultList[dieRoll]
    if isinstance(rolledResult, dict):
        return rollOnTable(rolledResult)
    else:
        return rolledResult



loadTables("classes.yaml")
for i in range(21):
    a = rollOnTable(data['tables']['classes'])
    print(a)




