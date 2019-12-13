#!/usr/bin/env python
import yaml
import random
import copy
import argparse

from .personalityGenerator import create_personality_string
from .dice import roll
from .character import Character

# ackstools 0.3 Dungeon compatible build
# TODO: replace strings to yaml with static vars
CLASSES = 'classes'
HD = 'hd'
MOD = 'modifiers'
SV = 'save'
AP = 'attackprog'
AB = 'abilities'
MR = 'minreq'
PROFS = 'profs'
GPROFS = 'generalproficiencies'
PPROG = 'proficiencyprogression'


def rollCharacters(cls, lvl, number, data):
    charList = []
    for i in range(0, number):
        charList.append(createCharacter(cls, lvl, data))

    return charList


def createCharacter(cls, lvl, data):

    c = Character
    c.level = lvl

    character_class = cls

    if character_class == "random":
        character_class = random.choice(list(data[CLASSES].keys()))

    if not character_class in data[CLASSES]:
        return "this is not a class"

    c.cclass = cls

    # roll ability scores
    c.strength = roll("3d6")
    c.dexterity = roll("3d6")
    c.constitution = roll("3d6")
    c.int = roll("3d6")
    c.wis = roll("3d6")
    c.cha = roll("3d6")

    # get base stats
    c.mv = 120
    c.hd = data[CLASSES][c.cclass][HD]
    c.hp = roll(str(lvl) + c.hd) + c.level * data[MOD][c.constitution]
    c.ini = data[MOD][c.dexterity]
    c.al = random.choice(['N', 'N', 'N', 'N', 'N', 'N', 'L', 'L', "L", 'C'])

    c.sv = data[CLASSES][c.cclass][SV] + str(lvl)
    if data[MOD][c.wis] < 0:
        c.sv = c.sv + str(data[MOD][c.wis])
    if data[MOD][c.wis] > 0:
        c.sv = c.sv + "+" + str(data[MOD][c.wis])

    # get base attack throw and damage bonus
    c.at = data[CLASSES][c.cclass][AP][c.level] - int(data[MOD][c.strength])
    c.mat = data[CLASSES][c.cclass][AP][c.level] - int(data[MOD][c.dexterity])
    c.cdb = data[MOD][c.strength]
    c.mdb = 0

    # check if char is caster
    spellcaster = False
    if 'spellcasting' in data[CLASSES][character_class]: spellcaster = True

    # check minimum requirements to belong to class
    for i in data[CLASSES][c.cclass][MR]:
        if getattr(c, i) < data[CLASSES][character_class][MR][i]:
            return createCharacter(c.cclass, c.level, data)

    # get abilities and write them into the stat array
    #level hochzählen. für jedes level in der klasse die abilities uplooken und auf stats draufrechnen
    for i in range(1, c.level + 1):
        if i in data[CLASSES][c.cclass][AB]:
            for x in data[CLASSES][c.cclass][AB][i]:
                c.abilities.setdefault(x, 0)
                c.abilities[x] += 1

    # get some random proficiencies
    no_of_class_profs = sum(c.level >= i for i in data[CLASSES][c.cclass]['profprog'])
    no_of_gen_profs = sum(c.level >= i for i in data['profprogressions']['general'])
    if data[MOD][c.int] > 0:
        no_of_gen_profs += data[MOD][c.int]

    tempAP = copy.deepcopy(data[PROFS])
    tempCP = copy.deepcopy(data[CLASSES][c.cclass][PROFS])
    tempGP = copy.deepcopy(data[GPROFS])
    #get class proficiencies and delete them from the temp. list if they were chosen too often
    for i in range(0, no_of_class_profs):
        p = random.choice(tempCP)
        tempAP[p][max] += -1
        if tempAP[p][max] == 0:
            tempCP.remove(p)
            if p in tempGP:
                tempGP.remove(p)
        c.proficiencies.setdefault(p, 0)
        c.proficiencies[p] += 1

    #get general profs and delete them as above
    for i in range(0, no_of_gen_profs):
        p = random.choice(tempGP)
        tempAP[p] += -1
        if tempAP[p] == 0:
            tempGP.remove(p)
            if p in tempCP:
                tempCP.remove(p)
        c.proficiencies.setdefault(p, 0)
        c.proficiencies[p] += 1

    # modify character stats according to the yaml document
    for charAbility in c.abilities:
        for ability in charAbility['modifies'].keys():
            for charLevel in range(1, c.level+1):
                if charLevel in charAbility['modifies'][charAbility]:
                    setattr(c,ability,getattr(c,ability)+1)


    for charProficiency in character['proficiencies']:
        if charProficiency in list(data['statmods']):
            for charLevel in range(1, character['lvl'] + 1):
                if charLevel in data['statmods'][charProficiency]:
                    for stat_to_modify in list(data['statmods'][charProficiency][charLevel]):
                        rank_of_modifying_ability = character['proficiencies'][charProficiency]
                        rank_of_modifying_ability = rank_of_modifying_ability * \
                                                    data['statmods'][charProficiency][charLevel][stat_to_modify]
                        if stat_to_modify in character:
                            character[stat_to_modify] = int(character[stat_to_modify]) + rank_of_modifying_ability
                        rank_of_modifying_ability = 0

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

    return character


def run(args):
    with open("./classes.yaml", 'r') as stream:
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
