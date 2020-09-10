from Tools.chargen.character import Character
from Tools.tableroller import rollOnTable, rollOnTable_string
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

        #print(clazz)
        for ablt in clazz.get('primerequisites', []):
            for i in range(getabilitymodifier(abilities.get(ablt, 0)) * 2):
                poss_cls_choice.append(clscop)

        for path in clazz.get('path', []):
            for ablt in clazz.get('primerequisites', {}).get('path', {}).get(path, {}):
                for i in range(getabilitymodifier(abilities.get(ablt, 0)) * 2):
                    clscop.get('path', []).append(path)

        poss_cls_choice.append(clscop)
    if not poss_cls_choice:
        choose_random_class_weighted(classdict, roll_random_stats())
        return

    choice_class = random.choice(poss_cls_choice)
    choice_path = random.choice(choice_class.get("path", [None]))
    choice_class['path'] = choice_path

    return choice_class


def roll_party(number, fluctuate, sourcedict, level, clazz = None,
               ethnicity = None, gender = None, name = None, alignment = None, path = None):
    characterlist = []
    fluctuation = [-2,-1,0,1,2]
    for i in range(number):
        deviation = 0
        adj_level = level
        if fluctuate:
            deviation = random.choice(fluctuation)
            adj_level = min(max(1,level+deviation),14)
        character = roll_character(sourcedict, adj_level, clazz, ethnicity, gender, name, alignment, path)
        #todo: hotfix weil character manchmal none ist. keine ahnung wieso...
        if character: characterlist.append(character)

    return characterlist


def roll_character(sourcedict, level, clazz = None, ethnicity = None, gender = None, name = None, alignment = None, path = None, scores = None):
    def apply_path(class_dict: dict, path):
        if path:
            if not(path in class_dict.get('path', '')):
                raise Exception("this class does not have the path " + str(path))
            del class_dict['path']
            for k in class_dict:
                if isinstance(class_dict[k],dict):
                    if 'path' in class_dict[k]:
                        chosenpath = class_dict[k]['path'][path]
                        class_dict[k] = chosenpath
        elif not(path):
            if 'path' in class_dict:
                raise Exception('this class has to choose a path')
        return class_dict

    if not scores: scores = roll_random_stats()
    # preprocessing and selection of class & path
    dict_of_classes = sourcedict['classes']

    # klasse wählen. wenn die klasse nicht im dict existiert ist es eine zufällige
    if clazz not in dict_of_classes:
        cls = choose_random_class_weighted(dict_of_classes,scores)
        while cls == None:
            cls = choose_random_class_weighted(dict_of_classes,roll_random_stats())
        clazz = cls.get('class')
        path = cls.get('path', None)

    class_dict = copy.deepcopy(dict_of_classes[clazz])

    # pfad wählen oder falsch gesetzten pfad ignorieren
    if path:
        # wenn pfad gesetzt, überprüfe ob das überhaupt gültig ist. wenn nein path = None
        path = (path if path in class_dict.get('path', []) else None)
    else:
        # wenn kein pfad gesetzt, überprüfe ob klasse einen path haben muss. wenn ja nimm zufälligen
        path = random.choice(dict_of_classes.get(clazz,{}).get('path', [None]))

    if not clazz:
        roll_character(sourcedict, level, clazz, ethnicity, gender, name, alignment, path)
        return

    # wenn pfad gewählt: class dict so modifizieren, dass alle path branches rausgeworfen werden
    path_name = ''
    if path:
        class_dict = apply_path(class_dict, path)
        path_name = " (" + str.capitalize(path) + ")"

    # ethnicity wählen. wenn spezifiziert gucken ob valide, wenn nicht zufällige wählen.
    ethnicity_dict = sourcedict['ethnicity']
    if 'ethnicity' in class_dict:
        ethnicity = (ethnicity if ethnicity in class_dict.get('ethnicity', []) else random.choice(
                class_dict.get('ethnicity', list(ethnicity_dict.keys()))))
    if ethnicity not in ethnicity_dict:
        ethnicity = random.choice(list(ethnicity_dict.keys()))

    if 'gender' in class_dict: gender = class_dict.get('gender')
    if gender not in ['male', 'female']: gender = random.choice(['male', 'female'])

    #print(clazz)
    #print(ethnicity)
    if not name:
        name = random.choice(ethnicity_dict[ethnicity][gender + " names"])
        if 'surnames' in ethnicity_dict[ethnicity]:
            name = name + " " + random.choice(ethnicity_dict[ethnicity]['surnames'])

    if not alignment: alignment = random.choice(['C', 'L', 'L', 'N', 'N', 'N'])

    m_items = roll_magical_items(level, sourcedict)
    gen_prof_prog = sourcedict['proficiencyprogression']['general']


    c = Character()
    generalproficiencies = copy.deepcopy(sourcedict['generalproficiencies'])
    c.createFromScratch(class_dict, generalproficiencies, gen_prof_prog, sourcedict['desctables'], ethnicity, name, clazz, level,
                        alignment, gender, scores, m_items, path_name)

    return c.__repr__()


def parse_magical_table_entry(entry):
    if isinstance(entry, dict):
        return parse_magical_item(entry)
    elif isinstance(entry, str):
        return parse_magical_item({"item": entry})
    elif isinstance(entry, list):
        r = []
        for e in entry:
            r.append(parse_magical_table_entry(e))
        return r


def parse_magical_item(object :dict):
    item = copy.deepcopy(rollOnTable(object.get("item")))
    if isinstance(item, str):
        item = {"name": item, "weight": 1}
    elif not isinstance(item, dict):
        raise Exception("item has to be str or dict!")

    item['name'] = rollOnTable_string(object.get('prefix','')) + item['name'] + rollOnTable_string(object.get('postfix',''))

    if 'mod' in object:
        for elem_key in object['mod']:
            if isinstance(object['mod'][elem_key],dict):
                for dict_key in object['mod'][elem_key]:
                    item[elem_key][dict_key] = item.get(dict_key,0) + object['mod'][elem_key][dict_key]
            elif isinstance(object['mod'][elem_key], int):
                item[elem_key] = item.get(elem_key,0) + object['mod'][elem_key]

    if 'add' in object:
        for elem_key in object['add']:
            item[elem_key] = object['add'][elem_key]
    return item


def roll_magical_items(level, data):
    common = data['tables']['treasure']['heroic magic']['common']
    uncommon = data['tables']['treasure']['heroic magic']['uncommon']
    rare = data['tables']['treasure']['heroic magic']['rare']
    very_rare = data['tables']['treasure']['heroic magic']['very rare']
    legendary = data['tables']['treasure']['heroic magic']['legendary']
    result= []

    def roll_on_mag_table(no_rolls, probability, table):
        items = []
        for i in range(no_rolls):
            if roll("1d100") <= level*probability:
                table_roll = parse_magical_table_entry(rollOnTable(table))
                if isinstance(table_roll,list):
                    items.extend(table_roll)
                else:
                    items.append(table_roll)
        return items

    result.extend(roll_on_mag_table(4, 10 * level, common))
    result.extend(roll_on_mag_table(3, 10 * level, uncommon))
    result.extend(roll_on_mag_table(2, 10 * level, rare))
    result.extend(roll_on_mag_table(1, 5 * level, very_rare))
    result.extend(roll_on_mag_table(1, 1 * level, legendary))

    return result


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

#stream = open("C:/Users/mhoh1/PycharmProjects/acksgen/generator_circle_of_dawn.yaml", 'r')
#data = yaml.safe_load(stream)

#roll_party(10000,True,data,14)