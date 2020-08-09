import math, random
from dice import roll

def test1():
    avg = 0
    ran = 100000
    for i in range(ran):
        x = str(roll("1d100"))
        if len(x) == 1:
            x = "0"+x


        if x[0]<x[1]:
            x = x[1]+x[0]

        avg = avg + int(x)

    return(avg/ran)

def test2():
    avg = 0
    ran = 100000
    for i in range(ran):
        res = 0
        x = roll("1d100")
        y = roll("1d100")

        if x < y:
            res = y
        else:
            res = x

        avg = avg + res
    return(avg/ran)

print(test1())
print(test2())