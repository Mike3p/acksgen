import re, os



def getProficienciesFromStrings():
    for k in os.listdir("./proflists"):
        f = open("./proflists/"+k, "r")
        o = open("./"+k+'_output.txt', "w+")
        text = f.read()
        text = text.replace('\n', ' ')
        combatTricks = []
        if re.search(r"Combat Trickery \((.*)\)", text):
            combatTricks = re.search(r"Combat Trickery \((.*)\)", text).group(1).split(", ")
        proficiencies = re.sub("Combat Trickery \(.*\), ", '', text).split(", ")

        if combatTricks:
            for i in combatTricks:
                proficiencies.append("Combat Trickery ("+i+")")

        for x in proficiencies:
            x = x.lower()
            x = x.replace(" ", "_")
            x = x.replace("(", "")
            x = x.replace(")", "")
            if x.endswith("*"):
                x = x[:-1]
            o.write("- *"+x+"\n")

getProficienciesFromStrings()
