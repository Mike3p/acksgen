from Tools.chargen2.character import Character
from Tools.tablerollerv2 import rollOnTable, rollOnTable_string
from Tools.dice import roll
import yaml, math, random, copy

def roll_random_character(sourcedict):
    classtable = sourcedict['tables']['classes']
    cls = rollOnTable_string(classtable)
    if 'ethnicity' in sourcedict[cls]: eth = random.choice(sourcedict[cls]['ethnicity'])
    else: eth = random.choice(sourcedict['ethnicity'].keys())
    if 'gender' in sourcedict[cls]: gdr = sourcedict[cls]['gender']
    else: gdr = random.choice(['male', 'female'])


def create_character(sourcedict, ethnicity, name, level, cclass, alignment, gender,
                     strength, dexterity, constitution, intelligence, wisdom, charisma, path = None):
    print(sourcedict)
    try:
        classDict = copy.deepcopy(sourcedict['classes'][cclass])
    except:
        raise Exception("This is an invalid class")

    c = Character()
    generalproficiencies = copy.deepcopy(sourcedict['generalproficiencies'])
    spells = copy.deepcopy(sourcedict['spells'])
    c.createFromScratch(classDict, generalproficiencies, sourcedict['desctables'], spells, ethnicity, name, cclass, level, alignment, gender,
                        strength, dexterity, constitution, intelligence, wisdom, charisma,
                        path)

    return c

def dump_character(character: Character):
    if not(hasattr(character, 'name')):
        character.name = 'unnamed'

    f = open(character.name+".yaml", "w")
    f.write(yaml.safe_dump(character.__dict__, default_flow_style=False))
    f.close()

def load_character(name: str):
    x = {}
    try:
        x = yaml.safe_load(open(name+".yaml", "r"))
    except:
        raise Exception("This character does not exist")
    c = Character()
    for k in x.keys():
        setattr(c, k, x[k])
    return c

stream = open("C:/Users/mhoh1/PycharmProjects/acksgenerator/newdata.yaml", 'r')
data = yaml.safe_load(stream)

for i in range(1):
    a = create_character(data, "ilian", "tristan", 7, "loremaster", "L", "male", 13, 13, 13, 13, 9, 9)
    dump_character(a)
    print(a)