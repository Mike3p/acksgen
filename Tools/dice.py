import random

def roll(dicecode):
    try:
        a = dicecode.split("d")
        number = int(a[0])
        die = int(a[1])
        result = 0
        for i in range(number):
            result = result + random.randint(1, die)
        return result
    except:
        return ("not a valid die code")
        
def getMod(dieRoll):
    if(dieRoll >= 18):
        return 3;
    elif(dieroll >= 16):
        return 2;
    elif(dieroll >= 13):
        return 1;
    elif(dieroll >= 9):
        return 0;
    elif(dieroll >= 6):
        return -1;
    elif(dieroll >= 4):
        return -2;
    else
        return -3;