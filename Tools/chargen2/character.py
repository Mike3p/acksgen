import yaml, math, random
from Tools.dice import roll
from Tools.tablerollerv2 import rollOnTable_string, rollOnTable
from Tools.chargen2.personalityGenerator import create_personality_string


# noinspection PyAttributeOutsideInit
class Character:

    # noinspection PyAttributeOutsideInit
    def createFromScratch(self, classdict, generalprofs, styletables, spelllist, ethnicity, name, cclass, level, alignment, gender,
                          strength, dexterity, constitution, intelligence, wisdom, charisma, pathname = None, prob_to_double_dip=20):
        # load dictionary with all relevant infos
        self.classdict: dict = classdict

        # ability scores
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

        # process class dict and apply paths
        self.pathname = pathname
        if pathname:
            if not(pathname in classdict.get('path', '')):
                raise Exception("this class does not have the path " + str(pathname))
            del self.classdict['path']
            for k in self.classdict:
                if isinstance(self.classdict[k],dict):
                    if 'path' in self.classdict[k]:
                        chosenpath = classdict[k]['path'][pathname]
                        classdict[k] = chosenpath
        if not(pathname):
            if 'path' in self.classdict:
                raise Exception('this class has to choose a path')

        # base attributes
        self.ethnicity = ethnicity
        self.name = name
        self.gender = gender
        self.cclass = cclass
        self.experiencepoints = 0
        self.level = 0
        self.maxlevel = self.classdict['maxlevel']
        self.hdtype = self.classdict['hd']
        self.mv = self.classdict['mv']
        self.basehp = 0
        self.alignment = alignment

        # miscellaneous
        self.numberofattacks = 1
        self.encumbrance = 0
        self.lightencumbrance = 6
        self.mediumencumbrance = 8
        self.heavyencumbrance = 11
        self.proficiencies = {}
        self.abilities = {}
        self.cleavesperlevel = self.classdict['cleavesperlevel']
        self.hpafter9 = self.classdict['hpafter9']


        # inventory
        self.weapons = {}
        self.armor = {}
        self.gear = {}

        # progression
        self.experienceforlevel = self.classdict['experienceforlevel']
        self.classproficiencylist = self.classdict['proficiencylist']
        self.generalproficiencylist = generalprofs
        self.attackprogression = self.classdict['attackprogression']
        self.savingthrowprogression = self.classdict['savingthrows']['progression']
        self.initialsaves = self.classdict['savingthrows']['initial']
        self.genprofprogression = [0, 0, 5, 9, 13]
        self.classprofprogression = self.classdict['proficiencyprogression']
        self.minimumrequirements = self.classdict['minimumrequirements']
        self.abilityprogression = self.classdict['abilityprogression']

        # spellcasting
        if 'spellprogression' in self.classdict:
            self.casterlevel = 0
            self.ceremonythrow = 11
            self.spellprogression = self.classdict['spellprogression']
            self.spelllist = spelllist
            self.spells = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        # descriptive
        self.description = ''
        self.style = ''
        self.features = ''
        self.personality = ''

        #todo not sure if there is a better solution. i need compute statistics in case of changing attributes, levels, proficiencies, etc.
        if self.intelligence >= 13:
            self.chooseProficiency("general", "random",prob_to_double_dip)
        if self.intelligence >= 16:
            self.chooseProficiency("general", "random",prob_to_double_dip)
        if self.intelligence >= 18:
            self.chooseProficiency("general", "random",prob_to_double_dip)

        # this is for normalmen
        self.getAbilitiesForCurrentLevel(prob_to_double_dip)
        self.getEquipment()

        delattr(self,"classdict")

        self.levelup(level)

        # add looks. depends on charisma mod.
        self.addLooks(styletables)
        self.personality = create_personality_string()

    def levelup(self, to:int):
        self.computeStatistics()
        for i in range(to):
            if self.level >= self.maxlevel:
                print("maxlevel reached")
                return

            # level, exp und base hp muss ich hier tracken weil davon ja alles berechnet wird
            self.level += 1
            if hasattr(self, "casterlevel"): self.casterlevel+=1
            if self.level < 9: self.basehp = self.basehp + roll("1"+self.hdtype)
            else: self.basehp = self.basehp + self.hpafter9
            self.experiencepoints = self.experienceforlevel[self.level-1]

            # außerdem muss ich hier die abilities und so zuteilen.
            self.getAbilitiesForCurrentLevel()

            # und zauber nicht vergessen
            self.getSpellsForCurrentLevel()

        # nach dem leveln berechnen wir die abilities!
        self.computeStatistics()

    def getAbilitiesForCurrentLevel(self, prob_to_double_dip = 25):
        lvl = self.level
        for entry in self.abilityprogression.get(lvl,{}):
            def chooseRandomAbility(abilitydict: dict):
                if not "choice" in abilitydict:
                    raise Exception("This dictionary does not describe an ability choice.")
                choicesmade = []
                numberofchoices = abilitydict['number']
                for i in range(numberofchoices):
                    choice = abilitydict['choice'].pop(random.randrange(len(abilitydict['choice'])))
                    if isinstance(choice, list):
                        choicesmade.extend(choice)
                    else:
                        choicesmade.append(choice)
                return choicesmade

            if 'choice' in entry:
                abilitiesfromchoice = chooseRandomAbility(entry)
                for a in abilitiesfromchoice:
                    self.addAbility(a)
            else:
                self.addAbility(entry)

        numberofgeneralprofs = sum(i == lvl for i in self.genprofprogression)
        for i in range(numberofgeneralprofs):
            self.chooseProficiency("general", "random", prob_to_double_dip)

        numberofclassprofs = sum(i == lvl for i in self.classprofprogression)
        for i in range(numberofclassprofs):
            self.chooseProficiency("class", "random", prob_to_double_dip)

    def addAbility(self, entry):
        if isinstance(entry, str):
            self.abilities[entry] = {"name": entry}
        elif (entry.get('type', '') == 'genprof') or (entry.get('type', '') == 'classprof'):
            self.giveProficiencyToCharacter(entry)
        else:
            self.abilities[entry['name']] = entry

    def chooseProficiency(self, type:str, proficiencyToChoose, prob_intent_doubledip = 0):
        if type == "class":
            chosenfrom: list = self.classproficiencylist
        elif type == "general":
            chosenfrom: list = self.generalproficiencylist
        else:
            raise Exception("type must be general or class")

        if not (chosenfrom):
            raise Exception("character has no choices left?")

        proficiency:dict = {}
        if proficiencyToChoose == "random":
            choice = random.randrange(len(chosenfrom))

            if roll("1d100") <= prob_intent_doubledip:
                profs_char_can_double_dip = []
                for key in self.proficiencies:
                    if self.proficiencies[key]['ranks'] < self.proficiencies[key]['max']:
                        profs_char_can_double_dip.append(self.proficiencies[key])
                if profs_char_can_double_dip:
                    choice = random.randrange(len(profs_char_can_double_dip))
                    prof_to_double_dip = profs_char_can_double_dip[choice]
                    print("character has double dipped " + prof_to_double_dip['name'])
                    self.giveProficiencyToCharacter(prof_to_double_dip)
                    return

            proficiency = chosenfrom[choice]

        else:
            for p in chosenfrom:
                if p['name'] == proficiencyToChoose:
                    proficiency = p

        if not proficiency:
            raise Exception("a proficiency of this name does not exist in the specified list: "+proficiencyToChoose)

        print("character has chosen proficiency: " + proficiency['name'])
        self.giveProficiencyToCharacter(proficiency)

    def giveProficiencyToCharacter(self, proficiency):
        profname = proficiency['name']
        if not (profname in self.proficiencies):
            self.proficiencies[profname] = proficiency
            self.proficiencies[profname]['ranks'] = 1
        else:
            self.proficiencies[profname]['ranks'] += 1

        if self.proficiencies[profname]['ranks'] >= self.proficiencies[profname]['max']:
            if proficiency in self.generalproficiencylist: self.generalproficiencylist.remove(proficiency)
            if proficiency in self.classproficiencylist: self.classproficiencylist.remove(proficiency)

    def getSpellsForCurrentLevel(self):
        if not(hasattr(self,"spellprogression")):
            return
        spellsperlevel = self.spellprogression[self.casterlevel]
        for spelllevel in spellsperlevel.keys():
            numberofspellstoget = spellsperlevel[spelllevel]+self.intmod - (len(self.spells.get(spelllevel,[])))
            spellChance = [34,33,33]
            if self.alignment == 'N': spellChance = [40, 90, 100]
            if self.alignment == 'L': spellChance = [60, 98, 100]
            if self.alignment == 'C': spellChance = [30, 60, 100]
            for j in range(numberofspellstoget):
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
                spell = random.choice(self.spelllist[spellColor][spelllevel]) + " (" + shortHand + ")"
                if not spell in self.spells[spelllevel]:
                    self.spells[spelllevel].append(spell)

    # noinspection PyAttributeOutsideInit
    def computeStatistics(self):
        #first compute basic modifications by leveling

        #ability score modifiers
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
                return 3
        self.strmod = getabilitymodifier(self.strength)
        self.dexmod = getabilitymodifier(self.dexterity)
        self.conmod = getabilitymodifier(self.constitution)
        self.intmod = getabilitymodifier(self.intelligence)
        self.wismod = getabilitymodifier(self.wisdom)
        self.chamod = getabilitymodifier(self.charisma)

        #AC und HP
        self.ac = 0 + self.dexmod
        self.hd = min(self.level,9)
        self.hp = self.basehp+(self.hd*self.conmod)

        #Angriffe und Kampfstats
        self.meleethrow = 11 - sum(i <= self.level for i in self.attackprogression) - self.strmod
        self.missilethrow = 11 - sum(i <= self.level for i in self.attackprogression) - self.dexmod
        self.meleedamage = self.strmod
        self.missiledamage = self.dexmod
        self.surprise = 3
        self.initiative = self.dexmod
        self.numberofcleaves = math.floor(self.cleavesperlevel * self.level)
        self.henchmen = 4+self.chamod
        if hasattr(self,"ceremonythrow"): self.ceremonythrow = 11 - self.casterlevel - self.wismod

        #calculate encumbrance and movement
        def getEncumbrance(items: dict):
            out = 0
            for i in items:
                out += items[i]['weight'] * items[i]['amount']
            return out
        weight = getEncumbrance(self.weapons) + getEncumbrance(self.armor) + getEncumbrance(self.gear)
        #encumbrance[0] is the stones, [1] is the #items of the next stone
        self.encumbrance = (weight//6, weight % 6)

        if self.encumbrance[0] >= 6:
            self.mv = 90
        elif self.encumbrance[0] >= 8:
            self.mv = 60
        elif self.encumbrance[0] >= 11:
            self.mv = 30

        #saving throws
        throwmod = sum(i <= self.level for i in self.savingthrowprogression) - self.wismod
        self.PP = self.initialsaves[0]-throwmod
        self.PD = self.initialsaves[1]-throwmod
        self.BB = self.initialsaves[2]-throwmod
        self.SW = self.initialsaves[3]-throwmod
        self.S  = self.initialsaves[4]-throwmod

        #then include gained abilities and so on
        def processAbilities(powerlist:dict):

            for powername in powerlist.keys():
                power = powerlist[powername]
                modifies = power.get('modifies', {})
                modifiedby = power.get('modifyingabilityscore', {})
                ranks = power.get('ranks', 1)
                levelprogression = power.get('levelprogression', [])

                levelofproficiency = sum(i <= self.level for i in levelprogression)

                for statistic in modifies.keys():
                    if hasattr(self,statistic):
                        setattr(self,statistic,getattr(self,statistic)+(modifies[statistic]*levelofproficiency))
                    if statistic in self.abilities.keys():
                        self.abilities[statistic]['throw'] = self.abilities[statistic]['throw'] + modifies[statistic]*levelofproficiency
                    if statistic in self.proficiencies.keys():
                        self.proficiencies[statistic]['throw'] = self.proficiencies[statistic]['throw'] + modifies[statistic]*levelofproficiency

                if power.get('throw', None):
                    power['throw'] = power['throw'] - levelofproficiency
                    power['throw'] = power['throw'] - max((ranks*4-4),0)
                    if power.get('modifiedby', None):
                        power['throw'] = power['throw'] - getattr(self,power['modifiedby'])

                if power.get('subskills', None):
                    for subskill in power['subskills'].keys():
                        power['subskills'][subskill] = power['subskills'][subskill] - max((ranks*4-4),0)

                for statistic in modifiedby:
                    power['throw'] = power['throw']+getattr(self,statistic) * modifiedby[statistic]

        processAbilities(self.proficiencies)
        processAbilities(self.abilities)

        #now include the equipment
        #armor

        #weapons

        #gear

        #todo das hier ganz am ende weil es auf base stats basiert die von abilities und so gemodded werden
        #masscombat
        self.leadershipability = self.henchmen
        self.zoneofcontrol = math.ceil(self.leadershipability / 2)
        self.strategicability = max(self.intmod, self.wismod) + \
                                (min(self.intmod, self.wismod) if min(self.intmod, self.wismod) < 0 else 0)
        self.moralemodifier = self.chamod
        self.unitmorale = self.chamod

    def __init__(self):
        pass

    def getEquipment(self):
        weapons = self.classdict['equipment']['weapons']
        armor = self.classdict['equipment']['armor']
        gear = self.classdict['equipment']['gear']

        def fillInventory(source):
            out = {}
            for entry in source:
                amount = roll(str(entry[1]))
                for i in range(amount):
                    item = rollOnTable(entry[0])
                    if item:
                        item.setdefault('amount',0)
                        item['amount'] +=1
                        out[item['name']] = item

            return out

        self.weapons = fillInventory(weapons)
        self.armor = fillInventory(armor)
        self.gear = fillInventory(gear)

    def addLooks(self, desctables):
        build = rollOnTable_string(desctables['human build'], self.strmod)
        eyecolor = rollOnTable_string(desctables['eye color'][self.ethnicity]).lower()
        haircolor = rollOnTable_string(desctables['hair color'][self.ethnicity]).lower()
        hairtype = rollOnTable_string(desctables['hair texture'][self.ethnicity]).lower()

        self.description = build + " " + self.gender + " " + self.ethnicity + " with " + eyecolor + " eyes and " + \
            haircolor + " hair of " + hairtype + " texture."


        chm = self.chamod
        if chm > 0:
            for i in range(chm):
                self.features = self.features + (rollOnTable_string(desctables['features']['positive']))+". "
        elif chm < 0:
            for i in range(abs(chm)):
                self.features = self.features + (rollOnTable_string(desctables['features']['negativ']))+". "
        else:
            for i in range(random.choice([1, 1, 1, 1, 1, 1, 1, 2, 2, 3])):
                self.features = self.features + (rollOnTable_string(desctables['features']['average']))+". "

        self.features = self.features.strip()

        for i in range(random.choice([0, 1, 1, 1, 1, 1, 2, 2, 2, 3])):
            if self.alignment == 'L':
                self.style = self.style + (rollOnTable_string(desctables['styles']['belongings lawful']))+". "
            elif self.alignment == 'C':
                self.style = self.style + (rollOnTable_string(desctables['styles']['belongings chaotic']))+". "
            else:
                self.style = self.style + (rollOnTable_string(desctables['styles']['belongings any']))+". "

        for i in range(len(self.style)):
            self.style = str.replace(self.style, '[GENDERPERS]', ('He' if self.gender == 'male' else 'She')).strip()
            self.style = str.replace(self.style, '[GENDERPOSS]', ('His' if self.gender == 'male' else 'Her')).strip()

    def __repr__(self):
        def formatSpells(spells):
            output = ""
            for i in spells:
                if spells[i]:
                    output = output + "L" + str(i) + ": ["
                    for j in spells[i]:
                        output += j + ", "
                    output = output[:-2] + "]; "
            output = output[:-2]
            return output

        def formatItems(items):
            output = ''
            for i in items:
                amount = (str(items[i]['amount'])+"x " if items[i]['amount'] > 1 else '')
                output += amount + i + ", "
            output = output[:-2]
            if output == '':
                output = 'None'
            return output

        def formatSkills(skills):
            output = ""
            for x in skills:
                rank = (" "+str(skills[x].get('ranks',1)) if skills[x].get('ranks',1) > 1 else '')
                throw = (" ("+str(x['throw'])+"+"+")" if 'throw' in x else '')
                output += x + rank + throw + ", "
            output = output[:-2]
            return output

        character = "<b>{}:</b> {} {}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha: {}; <b>XP:</b> {}\n" \
                    "<b>MV</b> {}, <b>AC</b> {}, <b>HD</b> {}, <b>hp</b> {}, <b>SP</b> {}+, <b>INI</b> {}, " \
                    "<b>PP</b> {}+, <b>PD</b> {}+, <b>BB</b> {}+, <b>SW</b> {}+, <b>S</b> {}+, <b>AL</b> {};\n" \
                    "<b>Attacks:</b> (<b>Melee:</b> {}+, {} dmg; <b>Missile:</b> {}+, {} dmg);\n" \
                    "<b>Weapons:</b> {}. " \
                    "<b>Armor:</b> {};\n" \
                    "<b>Class Abilities:</b> {};\n" \
                    "<b>Proficiencies:</b> {};\n" \
                    "<b>Equipment:</b> {}. {};"

        character = character.format(
            self.name, self.cclass, self.level, self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma, self.experiencepoints,
            self.mv, self.ac, self.hdtype, self.hp, self.surprise, self.initiative,
            self.PP, self.PD, self.BB, self.SW, self.S, self.alignment,
            self.meleethrow, self.meleedamage, self.missilethrow, self.missiledamage,
            formatItems(self.weapons), formatItems(self.armor), formatSkills(self.abilities), formatSkills(self.proficiencies), formatItems(self.gear), self.encumbrance)

        if hasattr(self,'casterlevel'):
            spellstring = "\n<b>Spells</b>: {};"
            spellstring = spellstring.format(formatSpells(self.spells))
            character = character + spellstring

        character = character + "\n<b>Personality:</b> " + self.personality

        if len(self.features) > 0:
            character = character + "\n<b>Features:</b> " + self.features

        if len(self.style) > 0:
            character = character + "\n<b>Style:</b> " + self.style

        return character
