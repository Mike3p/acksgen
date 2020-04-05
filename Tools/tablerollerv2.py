import yaml
from .dice import roll


def formatTable(table):
    formattedTable: dict
    formattedTable = {'die': table['die'], 'res': {}}
    tableResults = table['res']
    for i in tableResults:
        if "-" in str(i):
            x = i.split("-")
            dieCodes = list(range(int(x[0]), int(x[1]) + 1))
            for j in dieCodes:
                formattedTable['res'][int(j)] = tableResults[i]
        else:
            formattedTable['res'][int(i)] = tableResults[i]
    return formattedTable


def rollOnTable(table, mod=0, die=None):
    # initialize resultlist
    res = []
    if isinstance(table, dict):
        if 'name' in table:
            return table

    if isinstance(table, str):
        if '[ROLL]' in table:
            table = table.replace('[ROLL]', '')
            return roll(table)
        return table
    elif isinstance(table, list):
        for t in table:
            res.append(rollOnTable(t))
        return res

    # fill table with "missing keys"
    tab = formatTable(table)
    # check if custom die is specified and die roll falls into table range
    dieroll = (roll(die) if die else roll(tab['die']))
    dieroll += mod
    if dieroll < min(list(tab['res'].keys())):
        dieroll = min(list(tab['res'].keys()))
    elif dieroll > max(list(tab['res'].keys())):
        dieroll = max(list(tab['res'].keys()))

    rolledresult = tab['res'][dieroll]
    # return getTableResultList(rolledresult)
    return rollOnTable(rolledresult)


def rollOnTable_string(table, mod=0, die=None,):
    results = rollOnTable(table, mod, die)
    out = ''
    for r in results:
        if isinstance(r, list):
            for x in r:
                out = out + str(x)
        elif isinstance(r,dict):
            out = out + r.get('name', 'unnamed roll object')
        else:
            out = out + str(r)
    # print(out)
    return out

# loadTables("./data.yaml")
# print(data)
# for i in range(10):
#    print(getTableResultString(data['randomtables']['treasure']['test'])+"\n")
