#!/usr/bin/env python
import yaml
import random
import copy
import argparse

from personalityGenerator import create_personality_string
from dice import roll
from character import Character
from skill import Skill
from tableroller import rollOnTable


# ackstools 0.3 Dungeon compatible build
# TODO: replace strings to yaml with static vars


def loadCharacterFile(d: dict):
    global data
    try:
        data = d
    except yaml.YAMLError as exc:
        print(exc)


def rollCharacters(cls, baseLevel, number, deviation=False):
    global data
    charList = []
    for i in range(0, number):
        deviator = 0
        if deviation:
            deviator = rollOnTable({'die': '1d6', 'results': {1: -2, 2: -1, 3: 0, 4: 0, 5: 1, 6: 2}})
        charList.append(createCharacter(cls, baseLevel + deviator))

    return charList


def addSkills(c: Character):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities

    tempAllProfs = copy.deepcopy(allProfs)
    tempClassProfs = copy.deepcopy(classProfs)
    tempGeneralProfs = copy.deepcopy(genProfs)

    addAbilities(c, tempAllProfs, tempGeneralProfs, tempClassProfs)
    addProficiencies(c, tempAllProfs, tempGeneralProfs, tempClassProfs)

def addSkillToCharacter(c: Character, s: Skill, tap, tgp, tcp):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities

    if s.name in allProfs:
        tap[s.name]['max'] += -1
        if tap[s.name]['max'] <= 0:
            try: tcp.remove(s.name)
            except: pass
            try: tgp.remove(s.name)
            except: pass
        c.proficiencies.setdefault(s.name, s)
        c.proficiencies[s.name].ranks += 1
    else:
        c.abilities.append(s)


def addAbilities(c: Character, tap, tgp, tcp):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities

    # level hochzählen. für jedes level in der klasse die abilities uplooken und auf stats draufrechnen
    for i in range(1, c.lvl + 1):
        # i geht alle level des charakters durch
        if i in classAbilities:
            # true wenn charakter auf dem level ein ability bekommt
            for j in classAbilities[i]:
                try: ca = allAbilities[j]
                except: pass
                try: ca = allProfs[j]
                except: pass
                # iteriert über die abilities die der charakter auf dem level bekommt
                # erstellt einen skill mit allen nötigen infos
                ability = Skill(j, ca.get('type', ''), ca.get('throw', 0), ca.get('modifiedby', ''),
                                ca.get('modifies', {}), ca.get('progression', []))
                addSkillToCharacter(c, ability, tap, tgp, tcp)


def addProficiencies(c: Character, tap, tgp, tcp):
    # anzahl der proficiencies berechnen die den charakter zustehen
    no_of_class_profs = sum(c.lvl >= i for i in classProfProg)
    no_of_general_profs = sum(c.lvl >= i for i in genProfProg)

    if c.getIntMod() > 0:
        no_of_general_profs + c.getIntMod()

    def addProfs(x, profList, c):
        for i in range(x):
            rndProf = random.choice(profList)
            cp = allProfs[rndProf]
            proficiency = Skill(rndProf, cp.get('type', ''), cp.get('throw', 0), cp.get('modifiedby', ''),
                                cp.get('modifies', {}), cp.get('progression', []))
            addSkillToCharacter(c, proficiency, tap, tgp, tcp)

    addProfs(no_of_class_profs, tcp, c)
    addProfs(no_of_general_profs, tgp, c)

def createCharacter(cls, lvl):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities
    character_class = cls

    if character_class == "random":
        character_class = random.choice(list(data['classes'].keys()))

    if not character_class in data['classes']:
        return "this is not a class"

    # load confic dict into vars

    classDict = data['classes'][character_class]
    classHD = classDict['hd']
    classAttProg = classDict['attackprogression']
    classInitialSaves = classDict['saves']['initial']
    classSaveProg = classDict['saves']['progression']
    classMinReq = classDict['minreq']
    allProfs = data['profs']
    genProfs = data['generalprofs']
    classProfs = classDict['proficiencies']
    classProfProg = classDict['profprogression']
    genProfProg = data['profprogression']['general']
    allAbilities = data['abilities']
    classAbilities = classDict['abilities']

    # build character object
    c = Character()

    # set class and level
    c.cls = character_class
    c.lvl = lvl

    # roll ability scores
    c.strength = roll("3d6")
    c.dexterity = roll("3d6")
    c.constitution = roll("3d6")
    c.intelligence = roll("3d6")
    c.wisdom = roll("3d6")
    c.charisma = roll("3d6")

    # check minimum requirements to belong to class
    for i in classMinReq:
        if getattr(c, i) < classMinReq[i]:
            setattr(c, i, classMinReq[i])

    # get base stats
    c.mv = 120
    c.hd = classHD
    c.ac = c.getDexMod()
    c.hp = roll(str(lvl) + c.hd) + c.lvl * c.getConMod()
    c.ini = c.getDexMod()
    c.sp = 3
    c.al = random.choice(['N', 'N', 'N', 'L', "L", 'C'])

    # get saving throws
    increase = sum(i <= lvl for i in classSaveProg) + c.getWisMod()
    c.saves = [x - increase for x in classInitialSaves]

    # get base attack throw and damage bonus
    baseAttack = 10 - sum(i <= lvl for i in classAttProg)
    c.at = baseAttack - c.getStrMod()
    c.mat = baseAttack - c.getDexMod()
    c.cdb = c.getStrMod()
    c.mdb = 0

    # check if char is caster
    spellcaster = False
    if 'spellprog' in classDict: spellcaster = True

    # hier werden abilities und proficiencies behandelt
    addSkills(c)

    c.applyModifications()

    return c.getFormattedCharacter()

'''
    # if character is spellcaster, check progression
    if spellcaster:
        spellstring = ""
        intmod = 0
        if data['modifiers'][character['int']] > 0:
            intmod = data['modifiers'][character['int']]
        for i in data[CLASSES][character['cls']]['spellcasting'][character['lvl']]:
            spellstring += "L" + str(i) + ": " + str(
                data[CLASSES][character['cls']]['spellcasting'][character['lvl']][i] + intmod) + ", "

        spellstring = spellstring[:-2]
        character['spells'] = "Spells: " + spellstring + ";\n"

    # get armor
    temp = random.choice(data[CLASSES][character_class]['armor']['suit'])
    armor_suit = random.choice(list(temp.items()))

    temp = random.choice(data[CLASSES][character_class]['armor']['other'])
    armor_other = random.choice(list(temp.items()))

    ac_worn = armor_other[1] + armor_suit[1]
    character['ac'] = armor_other[1] + armor_suit[1] + data['modifiers'][dexterity]
    ac_string = "(" + armor_suit[0] \
                + (", " + armor_other[0] if armor_other[0] != "none" else "") \
                + (", Dex" if data['modifiers'][dexterity] != 0 else "") + ")";

    weight = ac_worn * 6
    # get some weapons
    equip = {}
    weapon_attack_string = ""
    weapon_damage_string = ""
    for i in range(0, random.randint(1, 3)):
        temp = random.choice(data[CLASSES][character_class]['weapons'])
        weapon = random.choice(list(temp.items()))
        weight = weight + weapon[1]['w']

        weapon_attack_throw = character['at']
        weapon_damage_roll_modifier = character['db']
        if 'type' in weapon[1]:
            if weapon[1]['type'] == 'ranged':
                # print(weapon[0] + " is ranged")
                weapon_attack_throw = character['mat']
                weapon_damage_roll_modifier = character['mdb']

        if 'mod' in weapon[1]:
            if 'at' in weapon[1]['mod']: weapon_attack_throw = weapon_attack_throw + weapon[1]['mod']['at']
            if 'mat' in weapon[1]['mod']: weapon_attack_throw = weapon_attack_throw + weapon[1]['mod']['mat']
            if 'db' in weapon[1]['mod']: weapon_damage_roll_modifier = weapon_damage_roll_modifier + weapon[1]['mod'][
                'db']

        weapon_attack_string += weapon[0] + " " + str(weapon_attack_throw) + "+ or "
        weapon_damage_string += weapon[1]['d'] + ("+" if weapon_damage_roll_modifier >= 0 else "") + str(
            weapon_damage_roll_modifier) + " or "
        equip.setdefault(weapon[0], 0)
        equip[weapon[0]] += 1
    weapon_attack_string = weapon_attack_string[:-4]
    weapon_damage_string = weapon_damage_string[:-4]
    # rint(weapon_attack_string)
    # print(weapon_damage_string)

    for i in range(0, random.randint(1, 10)):
        temp = random.choice(data[CLASSES][character_class]['items'])
        item = random.choice(list(temp.items()))
        weight = weight + item[1]
        equip.setdefault(item[0], 0)
        equip[item[0]] += 1
    weight = weight / 6

    if weight >= 5:
        mv += -30
    if weight >= 7:
        mv += -30
    if weight >= 10:
        mv += -30
    if weight > 20 + strength:
        mv += -30

    character['mv'] = mv

    character['equipment'] = equip
    equipment_formatted = ""
    for x in character['equipment']:
        if character['equipment'][x] > 1:
            equipment_formatted += str(character['equipment'][x]) + "x " + str(x) + ", "
        else:
            equipment_formatted += str(x) + ", "
    # equipment_formatted += ", "
    equipment_formatted = equipment_formatted[:-2]

    # some final minor formatting
    if character['db'] >= 0: character['db'] = "+" + str(character['db'])
    if character['mdb'] >= 0: character['mdb'] = "+" + str(character['mdb'])
    if character['ini'] >= 0: character['ini'] = "+" + str(character['ini'])

    # create personality
    pers = create_personality_string()

    character = "{}: {} {}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha {};\n" \
                "MV {}, AC {} {}, HD {}, hp {}, SP {}+, INI {}, Save {}, AL {};\n" \
                "Attacks: ({}) D {};\n" \
                "Special: {};\n" \
                "Proficiencies: {};\n" \
                "{}" \
                "Gear: {}. [{}s];\n" \
                "Personality: {}"
    character = character.format("Name", character['cls'], character['lvl'],
                                 character['str'], character['dex'], character['con'], character['int'],
                                 character['wis'], character['cha'],
                                 character['mv'], character['ac'], ac_string, character['hd'], character['hp'],
                                 character['sp'],
                                 character['ini'],
                                 character['save'], character['al'],
                                 weapon_attack_string, weapon_damage_string, abilities_formatted,
                                 proficiencies_formatted, character['spells'], equipment_formatted, "%.2f" % weight,
                                 pers)
    character = character.split("\n")
'''


def run(args):
    with open("../classes.yaml", 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    outfile = open(str(args.output), "w+")
    character_class = args.cls
    character_minlevel = args.min
    character_maxlevel = args.max
    no_of_characters = args.noc
    for i in range(0, no_of_characters):
        outfile.write(createCharacter(character_class, random.randint(character_minlevel, character_maxlevel), data))
        outfile.write("\n\n")


def main():
    parser = argparse.ArgumentParser(
        description="Create an ACKS character with class and level. Usage: chargen (number) (class) (level)")
    parser.add_argument("-out", help="output filename", dest="output", type=str, required=True)
    parser.add_argument("-n", help="number to generate", dest="noc", type=int, required=False, default=1)
    parser.add_argument("-c", help="class", dest="cls", type=str, required=False, default="random")
    parser.add_argument("-min", help="level", dest="min", type=int, required=False, default=1)
    parser.add_argument("-max", help="level", dest="max", type=int, required=False, default=random.randint(1, 14))
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

# todo: encode if stat must be switched.
