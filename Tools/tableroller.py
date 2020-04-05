import yaml
from .dice import roll

data = {}

def loadTables(s):
    global data
    with open("data.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

def formatTable(table):
    formattedTable: dict
    formattedTable = {'die': table['die'], 'res': {}}
    tableResults = table['res']
    for i in tableResults:
        if "-" in str(i):
            x = i.split("-")
            dieCodes = list(range(int(x[0]), int(x[1])+1))
            for j in dieCodes:
                formattedTable['res'][int(j)] = tableResults[i]
        else:
            formattedTable['res'][int(i)] = tableResults[i]
    return formattedTable

def getTableResultList(table, die = None):
    res = []

    if isinstance(table, str):
        if '[ROLL]' in table:
            table = table.replace('[ROLL]', '')
            return roll(table)
        return table
    elif isinstance(table, list) :
        for t in table:
            res.append(getTableResultList(t))
        return res
    f_table = formatTable(table)
    resultList = f_table['res']

    keyList = list(resultList.keys())

    if die:
        dieRoll = roll(die)
    else:
        dieRoll = roll(f_table['die'])
    if dieRoll < min(keyList):
        dieRoll = min(keyList)
    if dieRoll > max(keyList):
        dieRoll = max(keyList)

    rolledResults = resultList[dieRoll]
    #return getTableResultList(rolledResults)
    return getTableResultList(rolledResults)

def getTableResultString(table, die = None):
    results = getTableResultList(table, die)
    out = ''
    for r in results:
        if isinstance(r, list):
            for x in r:
                out = out + str(x)
        else:
            out = out + str(r)
    #print(out)
    return out


#loadTables("./data.yaml")
#print(data)
#for i in range(10):
#    print(getTableResultString(data['randomtables']['treasure']['test'])+"\n")