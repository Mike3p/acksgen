from Tools.chargen2.character import Character
from Tools.tablerollerv2 import rollOnTable, rollOnTable_string
from Tools.dice import roll
import yaml, random, copy


def roll_random_stats():
    abilities = {}
    abilities['strength'] = roll("3d6")
    abilities['dexterity'] = roll("3d6")
    abilities['constitution'] = roll("3d6")
    abilities['intelligence'] = roll("3d6")
    abilities['wisdom'] = roll("3d6")
    abilities['charisma'] = roll("3d6")
    return abilities


def getabilitymodifier(ability: int):
    if ability >= 18:
        return 3
    elif ability >= 16:
        return 2
    elif ability >= 13:
        return 1
    elif ability >= 9:
        return 0
    elif ability >= 6:
        return -1
    elif ability >= 4:
        return -2
    else:
        return -3


def choose_random_class_weighted(classdict, abilities: dict):
    if ("strength" not in abilities) or ("dexterity" not in abilities) or ("constitution" not in abilities) or \
            ("intelligence" not in abilities) or ("wisdom" not in abilities) or ("charisma" not in abilities):
        raise Exception("not a stat array!")

    poss_cls_choice = []
    for clskey in classdict:
        clscop = {}
        cls_valid = True
        clazz = classdict[clskey]
        for ablt in abilities:
            if (clazz.get('primerequisites', {}).get(ablt, 1) > abilities[ablt]) or \
                    (clazz.get('minrequisites', {}).get(ablt, 1) > abilities[ablt]):
                cls_valid = False

        if not cls_valid:
            continue

        clscop['class'] = clskey

        # if path in class check if it meets requirements. if so add it to the classchoice
        if 'path' in clazz: clscop['path'] = []
        for path in clazz.get('path', []):
            path_valid = True
            for ablt in abilities:
                if (clazz.get('primerequisites', {}).get('path', {}).get(path, {}).get(ablt, 1) > abilities[ablt]) or \
                        (clazz.get('minrequisites', {}).get('path', {}).get(path, {}).get(ablt, 1) > abilities[ablt]):
                    path_valid = False

            if not path_valid:
                continue
            clscop['path'].append(path)

        # if the class had paths but is not egligible for any, check next class
        if ('path' in clscop) and not (clscop.get('path', [])):
            continue

        for ablt in clazz.get('primerequisites'):
            for i in range(getabilitymodifier(abilities.get(ablt, 0)) * 2):
                poss_cls_choice.append(clscop)

        for path in clazz.get('path', []):
            for ablt in clazz.get('primerequisites', {}).get('path', {}).get(path, {}):
                for i in range(getabilitymodifier(abilities.get(ablt, 0)) * 2):
                    clscop.get('path', []).append(path)

        poss_cls_choice.append(clscop)
    if not poss_cls_choice:
        return None

    choice_class = random.choice(poss_cls_choice)
    choice_path = random.choice(choice_class.get("path", [None]))
    choice_class['path'] = choice_path

    return choice_class

def roll_party(number, fluctuate, sourcedict, level, clazz = "random",
               ethnicity = "random", gender = "random", name = "random", alignment = "random", path = "random"):
    characterlist = []
    fluctuation = [-2,-1,0,1,2]
    for i in range(number):
        deviation = 0
        if fluctuate:
            deviation = random.choice(fluctuation)
            level = min(max(1,level+deviation),14)
        characterlist.append(roll_random_character(sourcedict, level, clazz, ethnicity, gender, name, alignment, path))

    return characterlist


def roll_random_character(sourcedict, level, clazz = "random", ethnicity = "random", gender = "random", name = "random", alignment = "random", path = "random"):
    scores = roll_random_stats()
    classtable = sourcedict['classes']
    cls = {}
    if clazz == "random": cls = choose_random_class_weighted(classtable,scores)
    else: cls['class'] = clazz

    if not cls:
        roll_random_character(sourcedict, level, clazz, ethnicity, gender, name, alignment, path)
        return

    if path == "random": cls['path'] = random.choice(classtable.get(cls['class'],{}).get('path', [None]))
    else: cls['path'] = path
    ethtable = sourcedict['ethnicity']
    if ethnicity not in ethtable: ethnicity = random.choice(list(ethtable.keys()))
    if gender not in ['male', 'female']: gender = random.choice(['male', 'female'])
    if name == "random": name = random.choice(ethtable[ethnicity][gender + " names"])
    if alignment == "random": alignment = random.choice(['C', 'L', 'L', 'N', 'N', 'N'])

    return create_character(sourcedict, level, cls['class'], ethnicity, gender, name, alignment,
                            scores['strength'], scores['dexterity'], scores['constitution'],
                            scores['intelligence'], scores['wisdom'], scores['charisma'], cls.get('path'))


def create_character(sourcedict, level, clazz, ethnicity, gender, name, alignment,
                     strength, dexterity, constitution, intelligence, wisdom, charisma, path=None):
    # print(sourcedict)
    try:
        classdict = copy.deepcopy(sourcedict['classes'][clazz])

    except:
        raise Exception("This is an invalid class: " + clazz)

    c = Character()
    generalproficiencies = copy.deepcopy(sourcedict['generalproficiencies'])
    c.createFromScratch(classdict, generalproficiencies, sourcedict['desctables'], ethnicity, name, clazz, level,
                        alignment, gender,
                        strength, dexterity, constitution, intelligence, wisdom, charisma,
                        path)

    return c.__repr__()


def dump_character(character: Character):
    if not (hasattr(character, 'name')):
        character.name = 'unnamed'

    f = open(character.name + ".yaml", "w")
    f.write(yaml.safe_dump(character.__dict__, default_flow_style=False))
    f.close()


def load_character(name: str):
    x = {}
    try:
        x = yaml.safe_load(open(name + ".yaml", "r"))
    except:
        raise Exception("This character does not exist")
    c = Character()
    for k in x.keys():
        setattr(c, k, x[k])
    return c


#stream = open("C:/Users/mhoh1/PycharmProjects/acksgen/newdata.yaml", 'r')
#data = yaml.safe_load(stream)
