import yaml
from dice import roll

data = {}

def loadTables(s):
    global data
    with open(s, 'r') as stream:
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

def getTableResultList(table, modifier = 0):
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
    dieRoll = roll(f_table['die']) + modifier
    times = f_table.get('times', 1)
    if '[ROLL]' in str(times):
        times.replace('[ROLL]', '')
        times = roll(times)
    keyList = list(resultList.keys())
    if dieRoll < min(keyList):
        dieRoll = min(keyList)
    if dieRoll > max(keyList):
        dieRoll = max(keyList)
    rolledResults = resultList[dieRoll]
    #for i in range(times):
    #    rolledResults.append(resultList[dieRoll])
    #return getTableResultList(rolledResults)
    return getTableResultList(rolledResults)

def getTableResultString(table, modifier = 0):
    results = getTableResultList(table)
    out = ''
    for r in results:
        if isinstance(r, list):
            for x in r:
                out = out + str(x)
        else:
            out = out + str(r)
    print(out)
    return out


#loadTables("../data.yaml")
#for i in range(10):
#    print(rollOnTable(data['randomtables']['treasure']['a incidental']))