#!/usr/bin/env python
import yaml
import random
import copy
import argparse

from dice import roll
from charactergeneration.character import Character
from charactergeneration.item import Item, Weapon, Armor
from charactergeneration.skill import Skill
from tableroller import getTableResultString
from charactergeneration.personalityGenerator import create_personality_string, create_personality


# ackstools 0.3 Dungeon compatible build
# TODO: replace strings to yaml with static vars

data = {}


def loadCharacterFile(d: dict):
    global data
    try:
        data = d
    except yaml.YAMLError as exc:
        print(exc)


def rollCharacters(cls, baseLevel, number, deviation=False, ethnicity='random'):
    global data
    charList = []
    alignment = random.choice(['L', 'L', 'N', 'N', 'N', 'C'])
    print ('alignment: '+ alignment)
    for i in range(0, number):
        deviator = 0
        if deviation:
            deviator = random.choice([-2, -1, 0, 0, 1, 2])
            baseLevel = baseLevel + deviator

        if baseLevel < 0:
            baseLevel = 0

        charList.append(createCharacter(cls, baseLevel, ethnicity, alignment))

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
        tap.get(s.name)['max'] += -1
        if tap[s.name]['max'] <= 0:
            # print ("prof " + s.name + " empty!")
            try:
                tcp.remove(s.name)
            except:
                pass
            try:
                tgp.remove(s.name)
            except:
                pass
        c.proficiencies.setdefault(s.name, s)
        c.proficiencies[s.name].ranks += 1
    else:
        c.abilities.append(s)


def addAbilities(c: Character, tap, tgp, tcp):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities

    def makeChoice(choosee: dict):
        tempList = copy.deepcopy(choosee['choice'])
        abilities = []
        number_of_choices = choosee['number']
        for k in range(number_of_choices):
            selectedChoice = random.choice(tempList)
            try:
                tempList.remove(selectedChoice)
            except:
                print("tried to remove choice ability but failed")
            if isinstance(selectedChoice, list):
                abilities.extend(selectedChoice)
            else:
                abilities.append(selectedChoice)
        return abilities

    # level hochzählen. für jedes level in der klasse die abilities uplooken und auf stats draufrechnen
    for i in range(0, c.lvl + 1):
        # i geht alle level des charakters durch
        if i in classAbilities:
            # true wenn charakter auf dem level ein ability bekommt
            for j in classAbilities[i]:
                # j ist eine ability die man bekommt oder eine choice
                abilities = [j]

                if isinstance(j, dict) & ('choice' in j):
                    abilities = makeChoice(j)

                for l in abilities:
                    # l sind die abilities aus einer choice oder eine einzelne ability in ner liste
                    if l in allProfs:
                        ca = allProfs[l]
                    elif l in allAbilities:
                        ca = allAbilities[l]
                    else:
                        ca = {}
                    # iteriert über die abilities die der charakter auf dem level bekommt
                    # erstellt einen skill mit allen nötigen infos
                    ability = Skill(l, ca.get('type', ''), ca.get('throw', 0), ca.get('modifiedby', ''),
                                    ca.get('modifies', {}), ca.get('progression', []))
                    addSkillToCharacter(c, ability, tap, tgp, tcp)


def addProficiencies(c: Character, tap, tgp, tcp):
    # anzahl der proficiencies berechnen die den charakter zustehen
    genmod = c.getIntMod()
    if genmod < 0: genmod = 0
    no_of_class_profs = sum(c.lvl >= i for i in classProfProg)
    no_of_general_profs = sum(c.lvl >= i for i in genProfProg) + genmod

    if c.getIntMod() > 0:
        no_of_general_profs + c.getIntMod()

    def addProfs(x, profList, c):
        for i in range(x):
            rndProf = random.choice(profList)
            cp = allProfs[rndProf]
            proficiency = Skill(rndProf, cp.get('type', ''), cp.get('throw', 0), cp.get('modifiedby', ''),
                                cp.get('modifies', {}), cp.get('progression', []))
            # todo: add a modifyer that remembers the last prof choice. if it has a max. of > 2 gain the same proficiency again if it is on the prof list being checked
            addSkillToCharacter(c, proficiency, tap, tgp, tcp)

    addProfs(no_of_class_profs, tcp, c)
    addProfs(no_of_general_profs, tgp, c)


def addSpells(c):
    global classDict, allSpells
    if 'spellprogression' in classDict:
        spellChance = [33, 66, 100]
        classSpellProgression: dict = classDict['spellprogression']
        if c.al == 'N': spellChance = [40, 80, 100]
        if c.al == 'L': spellChance = [60, 95, 100]
        if c.al == 'C': spellChance = [30, 60, 100]

        for i in range(1, c.lvl + 1):
            spellsOnLevel = classSpellProgression.get(i)
            try:
                for spellLevel in spellsOnLevel:
                    amountOfSpells = spellsOnLevel.get(spellLevel)
                    if amountOfSpells > 0:
                        amountOfSpells += (c.getIntMod() if c.getIntMod() > 0 else 0)
                    spellList = []
                    for j in range(0, amountOfSpells):
                        x = roll("1d100")
                        spellColor = "grey"
                        shortHand = "g"
                        if x <= spellChance[0]:
                            spellColor = "white"
                            shortHand = "w"
                        elif x <= spellChance[1]:
                            spellColor = "grey"
                            shortHand = "g"
                        elif x <= spellChance[2]:
                            spellColor = "black"
                            shortHand = "b"
                        spell = random.choice(allSpells[spellColor][spellLevel]) + " ("+shortHand+")"
                        if not spell in spellList:
                            spellList.append(spell)
                    c.spells[spellLevel] = spellList
            except:
                pass


def addEquipment(c: Character):
    def chooseEquipment(equipmentList: dict):
        choices = {}
        for i in equipmentList:
            try:
                noOfItems = roll(i[1])
            except:
                noOfItems = 1
            if noOfItems < 0: noOfItems = 0
            for j in range(noOfItems):
                itemName = getTableResultString(i[0])
                if itemName:
                    choices.setdefault(itemName, 0)
                    choices[itemName] += 1
        return choices

    global classDict, data
    allEquipment = data['equipment']
    allWeapons = allEquipment['weapons']
    allArmor = allEquipment['armor']
    allAdvItems = allEquipment['adventuring equipment']
    classEquipment = classDict['equipment']
    classGear = classEquipment['gear']
    classWeapons = classEquipment['weapons']
    classArmor = classEquipment['armor']

    weaponChoices = chooseEquipment(classWeapons)
    for item in weaponChoices:
        itemDict = allWeapons.get(item)
        if itemDict:
            weapon = Weapon(weaponChoices.get(item), item, itemDict.get('weight', 0), itemDict.get('cost', 0),
                            itemDict.get('modifies', {}), itemDict.get('damage', '1d6'), itemDict.get('type', 'melee'))
            if 'ammo' in itemDict:
                classGear.append([itemDict['ammo'], 1])
            c.weapons.append(weapon)

    armorChoices = chooseEquipment(classArmor)
    for item in armorChoices:
        itemDict = allArmor.get(item)
        if itemDict:
            armor = Armor(armorChoices.get(item), item, itemDict.get('weight', 0), itemDict.get('cost', 0),
                          itemDict.get('ac', 1))
            c.armor.append(armor)

    itemChoices = chooseEquipment(classGear)
    for item in itemChoices:
        itemDict = allAdvItems.get(item)
        if itemDict:
            gear = Item(itemChoices.get(item), item, itemDict.get('weight', 0), itemDict.get('cost', 0))
            c.gear.append(gear)


def addLooks(character):
    character.build = getTableResultString(data['randomtables']['human build'])
    character.eyec = getTableResultString(data['randomtables']['eye color'][character.ethnicity]).lower()
    character.hairc = getTableResultString(data['randomtables']['hair color'][character.ethnicity]).lower()
    character.hairt = getTableResultString(data['randomtables']['hair texture'][character.ethnicity]).lower()
    chm = character.getChaMod()
    if chm > 0:
        for i in range(chm):
            character.features.append(getTableResultString(data['randomtables']['features']['positive']))
    elif chm < 0:
        for i in range(abs(chm)):
            character.features.append(getTableResultString(data['randomtables']['features']['negative']))
    else:
        for i in range(random.choice([1, 1, 1, 1, 1, 1, 1, 2, 2, 3])):
            character.features.append(getTableResultString(data['randomtables']['features']['average']))

    for i in range(random.choice([0,1,1,1,1,1,2,2,2,3])):
        if character.al == 'L':
            character.style.append(getTableResultString(data['randomtables']['styles']['belongings lawful']))
        elif character.al == 'C':
            character.style.append(getTableResultString(data['randomtables']['styles']['belongings chaotic']))
        else:
            character.style.append(getTableResultString(data['randomtables']['styles']['belongings any']))


def createCharacter(cls, lvl, ethnicity, partyAL = 'N'):
    global data, classDict, classAttProg, classInitialSaves, classSaveProg, classMinReq, \
        allProfs, genProfs, classProfs, classProfProg, genProfProg, allAbilities, classAbilities, allSpells

    character_class = cls
    if lvl == 0:
        character_class = 'normal man'

    # roll ability scores
    strength = roll("3d6")
    dexterity = roll("3d6")
    constitution = roll("3d6")
    intelligence = roll("3d6")
    wisdom = roll("3d6")
    charisma = roll("3d6")

    character = Character()

    character.al = 'N'

    character.strength = strength
    character.dexterity = dexterity
    character.constitution = constitution
    character.intelligence = intelligence
    character.wisdom = wisdom
    character.charisma = charisma

    #persönlichkeit bauen und verwerfen wenn der dude net den richtlinien entspricht.
    while True:
        character.personality = create_personality()
        pers = character.personality

        alignments = ['N', 'N']
        alFacts = [pers.get(('Honorable', 'Treacherous'), 0), pers.get(('Kind', 'Spiteful'), 0)]
        for f in alFacts:
            l = []
            if f > 0:
                l = ['L'] * abs(f)
            if f < 0:
                l = ['C'] * abs(f)
            alignments.extend(l)

        character.al = random.choice(alignments)
        if ((partyAL == 'L') & (character.al == 'C')) | ((partyAL == 'C') & (character.al == 'L')):
            continue
        else:
            print(partyAL + " " + character.al)
            break


    if character_class == "random":
        character_class = getTableResultString(data['randomtables']['classes'])

    # hier werden erst scores gewürfelt und dann geschaut welche klassen man nehmen darf
    # wir gucken uns alle klassen an und entfernen alle klassen und paths die die minrequs nicht erfüllen
    if character_class == "generate from scores":
        temp_classes = copy.deepcopy(data['classes'])
        temp_classlist = []
        for c_class in data['classes']:
            # minreqs checken für klasse c
            for ability in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                # falls die klasse einen pfad hat der minreqs beeinflusst: checken und pfade entfernen die diese
                # nicht erfüllen
                if 'path' in data['classes'][c_class]['minreq']:
                    for path in data['classes'][c_class]['minreq']['path']:
                        if data['classes'][c_class]['minreq']['path'][path].get(ability, 3) > locals()[ability]:
                            try:
                                temp_classes[c_class]['path'].remove(path)
                                print("deleted path " + str(path))
                            except: pass

                        for i in range(character.getModByString(ability) * 2):
                            temp_classes[c_class]['path'].append(path)

                if data['classes'][c_class]['minreq'].get(ability, 3) > locals()[ability]:
                    print("class " + str(c_class) + " has a lower " + ability + " than required.")
                    try:
                        del temp_classes[c_class]
                        print("deleted class " + str(c_class))
                        break
                    except: pass
                        # hat eine klasse positive modifier in ihren minreqs sollte die chance sie zu wählen höher sein



                if ability in data['classes'][c_class]['minreq']:
                    if not (c_class, temp_classes[c_class]) in temp_classlist:
                        temp_classlist.append((c_class, temp_classes[c_class]))
                    for i in range((character.getModByString(ability) * 2)):
                        temp_classlist.append((c_class, temp_classes[c_class]))

        #for i in temp_classlist:
        #   print(i[0])

        if temp_classlist:
            randomChoice = random.choice(temp_classlist)
            character_class = randomChoice[0]
            classDict = randomChoice[1]
        else:
            # wenn ein statblock keine einzige klasse sein darf nochmal würfeln
            createCharacter(character_class, lvl, ethnicity)

    else:
        classDict = data['classes'][character_class]
        classPath = ''

    if character_class not in data['classes']:
        return "this is not a class".split("\n")

    # check if class has multiple paths
    if 'path' in classDict:
        classPath = random.choice(classDict.get('path', ''))
        print("classpath chosen: " + classPath)
        newClassDict = copy.deepcopy(classDict)

        for key1 in classDict.keys():
            # print(key1)
            try:
                if 'path' in classDict[key1]:
                    x = classDict[key1]['path'][classPath]
                    del newClassDict[key1]['path']
                    if isinstance(x, dict):
                        for key2 in x.keys():
                            newClassDict[key1][key2] = x.get(key2, '')
                    else:
                        newClassDict[key1] = x
            except:
                pass
        character.path = classPath
        classDict = newClassDict
        # print(newClassDict)

    #todo nochmal angucken
    #load confic dict into vahrs
    classHD = classDict.get('hd', 'd6')
    classAttProg = classDict.get('attackprogression',[])
    classInitialSaves = classDict.get('saves').get('initial', ['20', '20', '20', '20', '20'])
    classSaveProg = classDict.get('saves').get('progression', [])
    classMinReq = classDict.get('minreq', '')
    allProfs = data.get('profs', [])
    genProfs = data.get('generalprofs', [])
    classProfs = classDict.get('proficiencies', [])
    classProfProg = classDict.get('profprogression', [])
    genProfProg = data.get('profprogression').get('general')
    allAbilities = data.get('abilities')
    classAbilities = classDict.get('abilities',[])
    allSpells = data.get('spells')

    # build add class path if exists

    possibleEthnicities = []

    if 'ethnicity' in classDict:
        if isinstance(classDict['ethnicity'], list):
            possibleEthnicities.extend(classDict['ethnicity'])
        else:
            possibleEthnicities.append(classDict['ethnicity'])
    else:
        possibleEthnicities = list(data['names'].keys())

    ethnicityChoice = random.choice(possibleEthnicities)

    if not ethnicity == 'random':
        ethnicityChoice = ethnicity

    character.ethnicity = ethnicityChoice

    if 'sex' in classDict:
        character.sex = classDict['sex']
    else:
        character.sex = random.choice(['male', 'female'])

    character.name = random.choice(data['names'][character.ethnicity][character.sex])

    # set class and level
    character.cls = character_class
    character.lvl = lvl

    # check minimum requirements to belong to class
    for c_class in classMinReq:
        while getattr(character, c_class) < classMinReq[c_class]:
            setattr(character, c_class, roll("3d6"))

    # get base stats
    character.mv = 120
    character.hd = classHD
    character.ac = character.getDexMod()
    character.hp = 0
    for i in range(character.lvl):
        hpgain = roll(str(1) + character.hd) + character.getConMod()
        if hpgain < 1: hpgain = 1
        character.hp = character.hp + hpgain
    if character.lvl == 0:
        character.hp = roll(str(1) + character.hd) + character.getConMod()
        if character.hp < 1: character.hp = 1
    character.ini = character.getDexMod()
    character.sp = 3
    character.ct = 11 - character.lvl

    # get saving throws
    increase = sum(i <= lvl for i in classSaveProg) + character.getWisMod()
    character.saves = [x - increase for x in classInitialSaves]

    # get base attack throw and damage bonus
    baseAttack = 11 - sum(i <= lvl for i in classAttProg)
    character.at = baseAttack - character.getStrMod()
    character.mat = baseAttack - character.getDexMod()
    character.cdb = character.getStrMod()
    character.mdb = 0

    # check if char is caster. if so add spells
    addSpells(character)

    # hier werden abilities und proficiencies behandelt
    addSkills(character)

    # hier wird equipment generiert
    addEquipment(character)

    # am ende alle mods von den skills und equip anwenden
    character.applyModifications()

    # jetzt noch aussehen und sowas machen
    addLooks(character)

    return character.getFormattedCharacter()


def run(args):
    with open("../../data.yaml", 'r') as stream:
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
        description="Create an ACKS character with class and level. Usage: pages (number) (class) (level)")
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
