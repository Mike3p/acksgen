from Tools.dice import roll


def rollInitiative(inis: list):
    inis.sort(key=lambda x: x[1], reverse=True)
    return inis


def getInitiativeAsString(inis: list):
    output = ''
    try:
        initiatives = rollInitiative(inis)
        output = []
        for r in initiatives:
            output.append(str(r[0]) + ": " + str(r[1]))
    except: pass

    return output
