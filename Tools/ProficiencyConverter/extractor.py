import re,os



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



def spellextractor():
    for k in os.listdir("./splists"):
        f = open("./splists/"+k, "r")
        o = open("./"+k+'_output.txt', "w+")
        lines = f.readlines()
        spells =[]

        pattern = re.compile(r'(....\(.*\))')

        for line in lines:
            splitline = line.split(' ',1)
            spells.append(splitline[1])

        for spell in spells:
            spell = pattern.sub(r"",spell)
            spell = spell.strip()
            spell = spell.replace(")","")
            spell = spell.replace("(", "")
            spell = spell.replace("*", "")
            spell = spell.replace(" trn", "")
            spell = spell.replace(" ill", "")
            spell = spell.replace(" dth", "")
            spell = spell.replace(" enc", "")
            spell = spell.replace(" nec", "")
            o.write("- "+spell+"\n")

getProficienciesFromStrings()