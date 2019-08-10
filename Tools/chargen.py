#!/usr/bin/env python
import yaml
import random
import copy
import argparse


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

def createCharacter(cls, lvl, data):

    character_class = cls

    if character_class == "random":
        character_class = random.choice(list(data['classes'].keys()))

    if not character_class in data['classes']:
        return "this is not a class"
    # roll ability scores
    strength = roll("3d6")
    dexterity = roll("3d6")
    constitution = roll("3d6")
    intelligence = roll("3d6")
    wisdom = roll("3d6")
    charisma = roll("3d6")

    # get base stats
    mv = 120
    hitdie = data['classes'][character_class]['hd']
    hp = roll(str(lvl) + hitdie) + lvl * data['modifiers'][constitution]
    initiative = data['modifiers'][dexterity]
    alignment = "N"

    saving_throw = data['classes'][character_class]['save'] + str(lvl)
    if data['modifiers'][wisdom] < 0:
        saving_throw = saving_throw + str(data['modifiers'][wisdom])
    if data['modifiers'][wisdom] > 0:
        saving_throw = saving_throw + "+" + str(data['modifiers'][wisdom])

    # get base attack throw and damage bonus
    attack_throw = data['classes'][character_class]['attackprog'][lvl] - int(data['modifiers'][strength])
    missile_throw = data['classes'][character_class]['attackprog'][lvl] - int(data['modifiers'][dexterity])
    damage_bonus = data['modifiers'][strength]

    # check if char is caster
    spellcaster = False
    if 'spellcasting' in data['classes'][character_class]: spellcaster = True

    stats = {"cls": character_class,
             "lvl": lvl,
             "str": strength,
             "dex": dexterity,
             "con": constitution,
             "int": intelligence,
             "wis": wisdom,
             "cha": charisma,
             "mv": mv,
             "ac": 0,
             "hd": hitdie,
             "hp": hp,
             "sp": 3,
             "ini": initiative,
             "save": saving_throw,
             "al": alignment,
             "at": attack_throw,
             "mat": missile_throw,
             "db": damage_bonus,
             "mdb": 0,
             "abilities": {},
             "proficiencies": {},
             "spells": "",
             "equipment": ""}

    # check minimum requirements to belong to class
    for i in data['classes'][character_class]['minreq']:
        if stats[i] < data['classes'][character_class]['minreq'][i]:
            return createCharacter(character_class, lvl, data)

    # get abilities and write them into the stat array
    for i in range(1, lvl + 1):
        if i in data['classes'][character_class]['abilities']:
            for x in data['classes'][character_class]['abilities'][i]:
                stats['abilities'].setdefault(x, 0)
                stats['abilities'][x] += 1

    # format abilities for output
    abilities_formatted = ""
    for x in stats['abilities']:
        abilities_formatted += x
        if stats['abilities'][x] > 1:
            abilities_formatted += " " + str(stats['abilities'][x])
        abilities_formatted += ", "
    abilities_formatted = abilities_formatted[:-2]

    # get some random proficiencies
    no_of_class_profs = sum(stats['lvl'] >= i for i in data['classes'][stats['cls']]['profprog'])
    no_of_gen_profs = sum(stats['lvl'] >= i for i in data['profprogressions']['G'])
    if data['modifiers'][stats['int']] > 0:
        no_of_gen_profs += data['modifiers'][stats['int']]

    tempAP = copy.deepcopy(data['allprofs'])
    tempCP = copy.deepcopy(data['classes'][stats['cls']]['profs'])
    tempGP = copy.deepcopy(data['genprofs'])
    for i in range(0, no_of_class_profs):
        p = random.choice(tempCP)
        tempAP[p] += -1
        if tempAP[p] == 0:
            tempCP.remove(p)
            if p in tempGP:
                tempGP.remove(p)
        stats['proficiencies'].setdefault(p, 0)
        stats['proficiencies'][p] += 1

    for i in range(0, no_of_gen_profs):
        p = random.choice(tempGP)
        tempAP[p] += -1
        if tempAP[p] == 0:
            tempGP.remove(p)
            if p in tempCP:
                tempCP.remove(p)
        stats['proficiencies'].setdefault(p, 0)
        stats['proficiencies'][p] += 1

    # format proficiencies for output
    proficiencies_formatted = ""
    for x in stats['proficiencies']:
        proficiencies_formatted += x
        if stats['proficiencies'][x] > 1:
            proficiencies_formatted += " " + str(stats['proficiencies'][x])
        proficiencies_formatted += ", "
    proficiencies_formatted = proficiencies_formatted[:-2]


    # modify character stats according to the yaml document
    for charAbility in stats['abilities']:
        if charAbility in list(data['statmods']):
            #print(charAbility + " is in statmods")
            for charLevel in range(1, stats['lvl'] + 1):
                if charLevel in data['statmods'][charAbility]:
                    for stat_to_modify in list(data['statmods'][charAbility][charLevel]):
                        rank_of_modifying_ability = stats['abilities'][charAbility]
                        value_of_stat_modifier = data['statmods'][charAbility][charLevel][stat_to_modify]
                        operand = ""
                        if str(value_of_stat_modifier).endswith("]"): #if modifier is ability score
                            operand = str(value_of_stat_modifier)[0:1]
                            #print("operand: "+operand)
                            #print(value_of_stat_modifier)
                            ability_score_used_as_mod = str(value_of_stat_modifier)[2:-1] #todo: nochma gucken warum der string abgefuckt is
                            #print(ability_score_used_as_mod)
                            value_of_stat_modifier = int(data['modifiers'][stats[ability_score_used_as_mod]])

                        final_modifier = rank_of_modifying_ability * value_of_stat_modifier

                        if operand == "-":
                            stats[stat_to_modify] = int(stats[stat_to_modify]) - int(final_modifier)
                        else:
                            stats[stat_to_modify] = int(stats[stat_to_modify]) + int(final_modifier)
                        rank_of_modifying_ability = 0

    for charProficiency in stats['proficiencies']:
        if charProficiency in list(data['statmods']):
            for charLevel in range(1, stats['lvl'] + 1):
                if charLevel in data['statmods'][charProficiency]:
                    for stat_to_modify in list(data['statmods'][charProficiency][charLevel]):
                        rank_of_modifying_ability = stats['proficiencies'][charProficiency]
                        rank_of_modifying_ability = rank_of_modifying_ability * data['statmods'][charProficiency][charLevel][stat_to_modify]
                        if stat_to_modify in stats:
                            stats[stat_to_modify] = int(stats[stat_to_modify]) + rank_of_modifying_ability
                        rank_of_modifying_ability = 0

    # if character is spellcaster, check progression
    if spellcaster:
        spellstring = ""
        intmod = 0
        if data['modifiers'][stats['int']] > 0:
            intmod = data['modifiers'][stats['int']]
        for i in data['classes'][stats['cls']]['spellcasting'][stats['lvl']]:
            spellstring += "L" + str(i) + ": " + str(
                data['classes'][stats['cls']]['spellcasting'][stats['lvl']][i] + intmod) + ", "

        spellstring = spellstring[:-2]
        stats['spells'] = "Spells: " + spellstring + ";\n"

    #get armor
    temp = random.choice(data['classes'][character_class]['armor']['suit'])
    armor_suit = random.choice(list(temp.items()))

    temp = random.choice(data['classes'][character_class]['armor']['other'])
    armor_other = random.choice(list(temp.items()))

    ac_worn = armor_other[1] + armor_suit[1]
    stats['ac'] = armor_other[1] + armor_suit[1] + data['modifiers'][dexterity]
    ac_string = "(" + armor_suit[0] \
                + (", " + armor_other[0] if armor_other[0] != "none" else "") \
                + (", Dex" if data['modifiers'][dexterity] != 0 else "") + ")";

    weight = ac_worn*6
    # get some weapons
    equip = {}
    weapon_attack_string = ""
    weapon_damage_string = ""
    for i in range(0, random.randint(1,3)):
        temp = random.choice(data['classes'][character_class]['weapons'])
        weapon = random.choice(list(temp.items()))
        weight = weight + weapon[1]['w']

        weapon_attack_throw = stats['at']
        weapon_damage_roll_modifier = stats['db']
        if 'type' in weapon[1]:
            if weapon[1]['type'] == 'ranged':
                #print(weapon[0] + " is ranged")
                weapon_attack_throw = stats['mat']
                weapon_damage_roll_modifier = stats['mdb']

        if 'mod' in weapon[1]:
            if 'at' in weapon[1]['mod']: weapon_attack_throw = weapon_attack_throw + weapon[1]['mod']['at']
            if 'mat' in weapon[1]['mod']: weapon_attack_throw = weapon_attack_throw + weapon[1]['mod']['mat']
            if 'db' in weapon[1]['mod']: weapon_damage_roll_modifier = weapon_damage_roll_modifier + weapon[1]['mod']['db']


        weapon_attack_string += weapon[0]+ " " + str(weapon_attack_throw)+"+ or "
        weapon_damage_string += weapon[1]['d']+("+" if weapon_damage_roll_modifier >= 0 else "")+str(weapon_damage_roll_modifier)+ " or "
        equip.setdefault(weapon[0], 0)
        equip[weapon[0]] += 1
    weapon_attack_string = weapon_attack_string[:-4]
    weapon_damage_string = weapon_damage_string[:-4]
    #rint(weapon_attack_string)
    #print(weapon_damage_string)

    for i in range(0, random.randint(1,10)):
        temp = random.choice(data['classes'][character_class]['items'])
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
    if weight > 20+strength:
        mv += -30

    stats['mv'] = mv

    stats['equipment'] = equip
    equipment_formatted = ""
    for x in stats['equipment']:
        if stats['equipment'][x] > 1:
            equipment_formatted += str(stats['equipment'][x]) + "x " +str(x)+", "
        else:
            equipment_formatted += str(x) + ", "
        #equipment_formatted += ", "
    equipment_formatted = equipment_formatted[:-2]

    # some final minor formatting
    if stats['db'] >= 0: stats['db'] = "+" + str(stats['db'])
    if stats['mdb'] >= 0: stats['mdb'] = "+" + str(stats['mdb'])
    if stats['ini'] >= 0: stats['ini'] = "+" + str(stats['ini'])

    character = "{}: {} {}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha {};\n" \
                "MV {}, AC {} {}, HD {}, hp {}, SP {}+, INI {}, Save {}, AL {};\n" \
                "Attacks: ({}) D {};\n" \
                "Special: {};\n" \
                "Proficiencies: {};\n" \
                "{}" \
                "Gear: {}. [{}s];"
    character = character.format("Name", stats['cls'], stats['lvl'],
                                 stats['str'], stats['dex'], stats['con'], stats['int'], stats['wis'], stats['cha'],
                                 stats['mv'], stats['ac'], ac_string, stats['hd'], stats['hp'], stats['sp'],
                                 stats['ini'],
                                 stats['save'], stats['al'],
                                 weapon_attack_string, weapon_damage_string, abilities_formatted,
                                 proficiencies_formatted, stats['spells'], equipment_formatted,"%.2f" % weight)

    return (character)

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
    no_of_characters= args.noc
    for i in range(0,no_of_characters):
        outfile.write(createCharacter(character_class, random.randint(character_minlevel,character_maxlevel), data))
        outfile.write("\n\n")


def main():
    parser = argparse.ArgumentParser(description="Create an ACKS character with class and level. Usage: chargen (number) (class) (level)")
    parser.add_argument("-out", help="output filename", dest="output", type=str, required=True)
    parser.add_argument("-n", help="number to generate", dest="noc", type=int, required=False, default=1)
    parser.add_argument("-c", help="class", dest="cls", type=str, required=False, default="random")
    parser.add_argument("-min", help="level", dest="min", type=int, required=False, default=1)
    parser.add_argument("-max", help="level", dest="max", type=int, required=False, default=random.randint(1,14))
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)
if __name__ == "__main__":
    main()

#todo: encode if stat must be switched.