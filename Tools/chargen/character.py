import math, random
from Tools.dice import roll
from Tools.tableroller import rollOnTable_string, rollOnTable
from Tools.chargen.personalityGenerator import create_personality_string


# noinspection PyAttributeOutsideInit
class Character:

    # noinspection PyAttributeOutsideInit
    def createFromScratch(self, classdict, generalprofs, gen_prof_prog, styletables, ethnicity, name, cclass, level, alignment, gender,
                          scores, mag_it, path = '', prob_to_double_dip=20):


        # load dictionary with all relevant infos
        self.classdict: dict = classdict
        # ability scores
        self.strength = scores.get('strength',10)
        self.dexterity = scores.get('dexterity',10)
        self.constitution = scores.get('constitution',10)
        self.intelligence = scores.get('intelligence',10)
        self.wisdom = scores.get('wisdom',10)
        self.charisma = scores.get('charisma',10)

        # for class name
        self.pathname = path

        # base attributes
        self.ethnicity = ethnicity
        self.name = name
        self.gender = gender
        self.cclass = cclass
        self.class_name = classdict.get('name', self.cclass)
        self.experiencepoints = 0
        self.level = 0
        self.maxlevel = self.classdict['maxlevel']
        self.hdtype = self.classdict['hd']
        self.mv = self.classdict['mv']
        self.mod_mv = self.mv
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
        self.magical_items = {}
        self.magical_item_rolls = mag_it

        # progression
        self.experienceforlevel = self.classdict['experienceforlevel']
        self.classproficiencylist = self.classdict['proficiencylist']
        self.generalproficiencylist = generalprofs
        self.attackprogression = self.classdict['attackprogression']
        self.savingthrowprogression = self.classdict['savingthrows']['progression']
        self.initialsaves = self.classdict['savingthrows']['initial']
        self.genprofprogression = gen_prof_prog
        self.classprofprogression = self.classdict['proficiencyprogression']
        self.primerequisites = self.classdict.get('primerequisites', [])
        self.minrequisites = self.classdict.get('minrequisites',[])
        self.abilityprogression = self.classdict['abilityprogression']

        for r in [self.minrequisites, self.primerequisites]:
            for a in r:
                while getattr(self, a) < r[a]:
                    setattr(self, a, roll("3d6"))

        # spellcasting
        if 'magictypes' in self.classdict:
            self.casterlevel = 0
            self.ceremonythrow = 11
            self.magictypes = self.classdict['magictypes']
            self.casterfraction = self.classdict.get('casterfraction', 1)
            self.spells = {}
            for magictype in self.magictypes:
                mname = magictype['name']
                self.spells[mname] = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
            self.spellprogressions = {}
            for mt in self.magictypes:
                self.spellprogressions[mt['name']] = {"progression": mt['progression'], "mode": mt['mode']}

        # descriptive
        self.description = ''
        self.style = ''
        self.features = ''
        self.personality = ''

        #todo not sure if there is a better solution. i need compute statistics in case of changing attributes, levels, proficiencies, etc.
        if self.intelligence >= 13:
            self.chooseProficiency(self.generalproficiencylist, "random", prob_to_double_dip)
        if self.intelligence >= 16:
            self.chooseProficiency(self.generalproficiencylist, "random", prob_to_double_dip)
        if self.intelligence >= 18:
            self.chooseProficiency(self.generalproficiencylist, "random", prob_to_double_dip)

        # this is for normalmen
        self.getAbilitiesForCurrentLevel(prob_to_double_dip)
        self.get_equipment()
        #self.get_magical_items(level)

        delattr(self, "classdict")
        self.compute_statistics()
        if self.maxlevel == 0:
            self.basehp = self.basehp + max(1, roll("1" + self.hdtype) + self.conmod)
            self.hp = self.basehp
        self.levelup(level, prob_to_double_dip)

        # add looks. depends on charisma mod.
        self.add_looks(styletables)
        self.personality = create_personality_string()

    def levelup(self, to:int, prob_to_double_dip):

        for i in range(self.level,to):
            if self.level >= self.maxlevel:
                return

            # level, exp und base hp muss ich hier tracken weil davon ja alles berechnet wird
            self.level += 1
            if hasattr(self, "casterlevel"): self.casterlevel = math.floor(self.level / self.casterfraction)
            if self.level < 9: self.basehp = self.basehp + max(1,roll("1"+self.hdtype)+self.conmod)
            else: self.basehp = self.basehp + self.hpafter9
            self.experiencepoints = self.experienceforlevel[self.level-1]

            # außerdem muss ich hier die abilities und so zuteilen.
            self.getAbilitiesForCurrentLevel(prob_to_double_dip)

            # und zauber nicht vergessen
            self.getSpellsForCurrentLevel()

        # nach dem leveln berechnen wir die abilities!
        self.compute_statistics()

    def getAbilitiesForCurrentLevel(self, prob_to_double_dip = 20):
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
            self.chooseProficiency(self.generalproficiencylist, "random", prob_to_double_dip)

        numberofclassprofs = sum(i == lvl for i in self.classprofprogression)
        for i in range(numberofclassprofs):
            self.chooseProficiency(self.classproficiencylist, "random", prob_to_double_dip)

    def addAbility(self, entry):
        if isinstance(entry, str):
            self.abilities[entry] = {"name": entry}
        elif (entry.get('type', '') == 'genprof') or (entry.get('type', '') == 'classprof'):
            self.giveProficiencyToCharacter(entry)
        elif ('spell' in entry):
            self.spells[entry['type']][entry['level']].append(entry['spell'])
        else:
            self.abilities[entry['name']] = entry

    def chooseProficiency(self, chosenfrom, prof_to_choose, prob_intent_doubledip = 0):
        # if type == "classprof":
        #     chosenfrom: list = self.classproficiencylist
        # elif type == "genprof":
        #     chosenfrom: list = self.generalproficiencylist
        # else:
        #     raise Exception("type must be general or class")

        # if not (chosenfrom):
        #     raise Exception("character has no choices left?")

        proficiency:dict = {}
        if prof_to_choose == "random":
            choice = random.randrange(len(chosenfrom))

            if roll("1d100") <= prob_intent_doubledip:
                profs_char_can_double_dip = []
                for key in self.proficiencies:
                    prof_in_correct_list = False
                    for item in chosenfrom:
                        if item['name'] == self.proficiencies[key]['name']:
                            prof_in_correct_list = True

                    if (self.proficiencies[key]['ranks'] < self.proficiencies[key]['max']) & prof_in_correct_list:
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
                if p['name'] == prof_to_choose:
                    proficiency = p

        if not proficiency:
            raise Exception("a proficiency of this name does not exist in the specified list: " + prof_to_choose)

        #print("character has chosen proficiency: " + proficiency['name'])
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
        if not(hasattr(self,"spells")):
            return

        for magictype in self.magictypes:
            spellsperlevel = magictype['progression'].get(self.casterlevel,{1: 0})
            mname = magictype['name']
            #self.spells[mname] = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
            for spelllevel in spellsperlevel.keys():
                #rechnet aus wieviele zauber man noch zu bekommen hat
                numberofspellstoget = spellsperlevel[spelllevel]+max(self.intmod,0) - (len(self.spells.get(mname, {}).get(spelllevel, [])))
                c_spell_list = magictype['list']

                if "divine" in str.lower(mname):
                    if numberofspellstoget > 0:
                        self.spells[mname][spelllevel].extend(c_spell_list.get(spelllevel,[]))
                        if spelllevel in c_spell_list:
                            c_spell_list.pop(spelllevel)
                else:
                    for j in range(numberofspellstoget):

                        al = self.alignment

                        if al in c_spell_list:
                            spell = random.choice(rollOnTable(c_spell_list[al])[spelllevel])
                        elif ('die' in c_spell_list) & ('res' in c_spell_list):
                            spell = random.choice(rollOnTable(c_spell_list)[spelllevel])
                        else: spell = random.choice(c_spell_list[spelllevel])

                        if spell not in self.spells[mname][spelllevel]:
                            self.spells[mname][spelllevel].append(spell)

    def get_equipment(self):
        equipment = self.classdict['equipment']

        def assign_to_character(item: dict):
            tags = item.get("tags",[])

            if "weapon" in tags:
                self.weapons[item['name']] = item
            elif "armor" in tags or "shield" in tags:
                self.armor[item['name']] = item
            else:
                self.gear[item['name']] = item

        for entry in equipment:
            amount = roll(str(entry[1]))
            for i in range(amount):
                item = rollOnTable(entry[0])
                if item:
                    item.setdefault('amount',0)
                    item['amount'] +=1
                    assign_to_character(item)

        for entry in self.magical_item_rolls:
            if entry.get("name") in self.magical_items:
                self.magical_items[entry.get("name")]["amount"] +=1
            else:
                self.magical_items[entry.get("name")] = entry
                self.magical_items[entry.get("name")]["amount"] = 1

    def add_looks(self, desctables):
        build = rollOnTable_string(desctables.get('build',{}).get(self.ethnicity,''), self.strmod).lower()
        skincolor = rollOnTable_string(desctables.get('skin color',{}).get(self.ethnicity,'')).lower()
        eyecolor = rollOnTable_string(desctables.get('eye color',{}).get(self.ethnicity,'')).lower()
        haircolor = rollOnTable_string(desctables.get('hair color',{}).get(self.ethnicity,'')).lower()
        hairtype = rollOnTable_string(desctables.get('hair texture',{}).get(self.ethnicity,'')).lower()

        if not(build + eyecolor + haircolor + hairtype+ skincolor):
            pass
        else:
            self.description = build + " " + self.gender + " " + str.capitalize(self.ethnicity) + " of " + skincolor + \
                               " complexion with " + eyecolor + " eyes and " + \
                               haircolor + " hair of " + hairtype + " texture."


        chm = self.chamod
        if chm > 0:
            for i in range(chm):
                self.features = self.features + (rollOnTable_string(desctables['features']['positive']))+". "
        elif chm < 0:
            for i in range(abs(chm)):
                self.features = self.features + (rollOnTable_string(desctables['features']['negative']))+". "
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

    # noinspection PyAttributeOutsideInit
    def compute_statistics(self):

        def process_abilities(powerlist: dict):

            def check_deavtivators(deactivator_list: str):
                deactivated = False
                for deactivator in deactivator_list:
                    attr = deactivator.split(":")[0]
                    key = deactivator.split(":")[1].split("=")[0]
                    arg = deactivator.split(":")[1].split("=")[1]

                    for elem in getattr(self, attr):
                        if (getattr(self, attr)[elem].get(key) == arg) or (arg in getattr(self, attr)[elem].get(key)):
                            deactivated = True
                return deactivated

            for powername in powerlist.keys():
                power = powerlist[powername]
                deactivators: str = power.get('deactivatedby', None)
                if deactivators:
                    if check_deavtivators(deactivators):
                        continue
                if power.get('throw'):
                    power['mod_throw'] = power['throw']
                modifies = power.get('modifies', {})
                modifiedby = power.get('modifyingabilityscore', {})
                ranks = power.get('ranks', 1)
                levelprogression = power.get('levelprogression', [])

                levelofproficiency = sum(i <= self.level for i in levelprogression)

                for statistic in modifies.keys():
                    if hasattr(self, statistic):
                        setattr(self, statistic, getattr(self, statistic) + (modifies[statistic] * levelofproficiency))
                    if statistic in self.abilities.keys():
                        self.abilities[statistic]['mod_throw'] = self.abilities[statistic]['mod_throw'] + modifies[
                            statistic] * levelofproficiency
                    if statistic in self.proficiencies.keys():
                        self.proficiencies[statistic]['mod_throw'] = self.proficiencies[statistic]['mod_throw'] + modifies[
                            statistic] * levelofproficiency

                if power.get('throw', None):
                    power['mod_throw'] = power['mod_throw'] - levelofproficiency
                    power['mod_throw'] = power['mod_throw'] - max((ranks * 4 - 4), 0)
                    if power.get('modifiedby', None):
                        power['mod_throw'] = power['mod_throw'] - getattr(self, power['modifiedby'])

                # if power.get('subskills', None):
                #     for subskill in power['subskills'].keys():
                #         power['subskills'][subskill] = power['subskills'][subskill] - max((ranks * 4 - 4), 0)

                for statistic in modifiedby:
                    power['mod_throw'] = power['mod_throw'] + getattr(self, statistic) * modifiedby[statistic]

        def process_equipment(equipmentlist: dict, ablt= []):
            setstats = {}
            for ik in equipmentlist:
                item = equipmentlist[ik]
                item_name = item.get("name", "unknown item")
                item_modifies = item.get("modifies", [])

                for statistic in item_modifies:
                    if not (ablt == [] or statistic in ablt): continue
                    modval: str = item_modifies[statistic]

                    if isinstance(modval, dict):
                        minvals = []
                        if "min" in modval.keys():
                            for v in modval.get("min",[]):
                                if isinstance(v,str):
                                    minvals.append(getattr(self,v,0))
                                elif isinstance(v,int):
                                    minvals.append(v)
                        maxvals = []
                        if "max" in modval.keys():

                            for v in modval.get("min", []):

                                if isinstance(v, str):
                                    maxvals.append(getattr(self,v, 0))
                                elif isinstance(v, int):
                                    maxvals.append(v)

                        if minvals: modval = "="+str(min(minvals))
                        if maxvals: modval = "="+str(max(maxvals))

                    if isinstance(modval, str):

                        if modval[0] == "=":
                            val = int(modval[1:])
                            if hasattr(self, statistic): setattr(self, statistic, val)
                            setstats[statistic] = True

                    if not setstats.get(statistic, False):
                        if hasattr(self, statistic):
                            setattr(self, statistic, getattr(self, statistic) + modval)
                        if statistic in self.abilities:
                            self.abilities[statistic]['mod_throw'] = self.abilities[statistic]['mod_throw'] + modval
                        if statistic in self.proficiencies:
                            self.proficiencies[statistic]['mod_throw'] = self.proficiencies[statistic]['mod_throw'] + modval

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

        self.strmod = getabilitymodifier(self.strength)
        self.dexmod = getabilitymodifier(self.dexterity)
        self.conmod = getabilitymodifier(self.constitution)
        self.intmod = getabilitymodifier(self.intelligence)
        self.wismod = getabilitymodifier(self.wisdom)
        self.chamod = getabilitymodifier(self.charisma)

        # equipment
        process_equipment(self.weapons, ['strmod', 'dexmod', 'conmod', 'intmod', 'wismod', 'chamod'])
        process_equipment(self.armor, ['strmod', 'dexmod', 'conmod', 'intmod', 'wismod', 'chamod'])
        process_equipment(self.gear, ['strmod', 'dexmod', 'conmod', 'intmod', 'wismod', 'chamod'])

        #AC und HP
        self.ac = 0 + self.dexmod
        self.acm = 0 + self.dexmod
        self.hd = min(self.level,9)
        #todo: this should add con mod per level on recompute to account for changing ability mods.
        self.hp = self.basehp

        #Angriffe und Kampfstats
        self.meleethrow = 11 - sum(i <= self.level for i in self.attackprogression) - self.strmod
        self.missilethrow = 11 - sum(i <= self.level for i in self.attackprogression) - self.dexmod
        self.meleedamage = self.strmod
        self.missiledamage = 0
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
        # encumbrance[0] is the stones, [1] is the #items of the next stone
        self.encumbrance = (weight//6, weight % 6)

        movement = 120
        if self.encumbrance[0] >= 11:
            movement = 30
        elif self.encumbrance[0] >= 8:
            movement = 60
        elif self.encumbrance[0] >= 6:
            movement = 90

        self.mod_mv = min(movement, self.mv)

        #saving throws
        throwmod = sum(i <= self.level for i in self.savingthrowprogression) - self.wismod
        self.PP = self.initialsaves[0]-throwmod
        self.PD = self.initialsaves[1]-throwmod
        self.BB = self.initialsaves[2]-throwmod
        self.SW = self.initialsaves[3]-throwmod
        self.S  = self.initialsaves[4]-throwmod

        #masscombat
        self.strategicability = max(self.intmod, self.wismod) + \
                                (min(self.intmod, self.wismod) if min(self.intmod, self.wismod) < 0 else 0)
        self.moralemodifier = self.chamod
        self.unitmorale = self.chamod

        # include gained abilities and so on
        process_abilities(self.proficiencies)
        process_abilities(self.abilities)

        # equipment
        process_equipment(self.weapons)
        process_equipment(self.armor)
        process_equipment(self.gear)

        self.leadershipability = self.henchmen
        self.zoneofcontrol = math.ceil(self.leadershipability / 2)

    def __init__(self):
        pass

    def __repr__(self):
        def formatSpells(magic_type, spells):
            output = ""
            for i in spells:
                if spells[i]:
                    number_of_casts = ''
                    if "ceremonial" in str.lower(self.spellprogressions[magic_type]['mode']):
                        number_of_casts = str(self.ceremonythrow + ((i-1)*2)) + "+"
                    else:
                        number_of_casts = "x"+str(self.spellprogressions[magic_type]['progression'][self.level][i])
                    output = output + "<b>L" + str(i)+"</b>" +" ("+number_of_casts +"): ["
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
                throw = (" ("+str(skills[x]['mod_throw'])+"+"+")" if ('mod_throw' in skills[x]) & (skills[x].get('mod_throw',21)<21) else '')
                output += x + rank + throw + ", "
            output = output[:-2]
            if output == "": output = "None"
            return output

        def formatBonus(bonus: int):
            if bonus > -1:
                return "+"+str(bonus)
            return str(bonus)

        def formatenc(enc):
            return "("+str(enc[0])+" st. & "+str(enc[1])+" it.)"


        character = "<b>{}:</b> {}{} {}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha: {}; <b>XP:</b> {}\n" \
                    "<b>MV</b> {}, <b>AC</b> {}, <b>HD</b> {}, <b>hp</b> {}, <b>SP</b> {}+, <b>INI</b> {}, " \
                    "<b>PP</b> {}+, <b>PD</b> {}+, <b>BB</b> {}+, <b>SW</b> {}+, <b>S</b> {}+, <b>AL</b> {};\n" \
                    "<b>Attacks:</b> (<b>Melee:</b> {}+, {} dmg; <b>Missile:</b> {}+, {} dmg);\n" \
                    "<b>Weapons:</b> {}. " \
                    "<b>Armor:</b> {};\n" \
                    "<b>Class Abilities:</b> {};\n" \
                    "<b>Proficiencies:</b> {};\n" \
                    "<b>Equipment:</b> {}. {};"

        character = character.format(
            self.name, self.class_name, self.pathname, self.level, self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma, self.experiencepoints,
            self.mod_mv, max(self.ac, self.acm), self.hdtype, self.hp, self.surprise, self.initiative,
            self.PP, self.PD, self.BB, self.SW, self.S, self.alignment,
            self.meleethrow, formatBonus(self.meleedamage), self.missilethrow, formatBonus(self.missiledamage),
            formatItems(self.weapons), formatItems(self.armor), formatSkills(self.abilities), formatSkills(self.proficiencies), formatItems(self.gear), formatenc(self.encumbrance))

        if hasattr(self,'casterlevel'):
            for mt in self.spells:
                spellstring = ""
                if self.spells[mt][1]:
                    spellstring = "\n<b>"+str.capitalize(mt)+" Spells</b>: {};"
                    spellstring = spellstring.format(formatSpells(mt, self.spells[mt]))
                character = character + spellstring

        character = character + "\n<b>Personality:</b> " + self.personality
        if self.description:
            character = character + "\n<b>Description:</b> " + str.capitalize(self.description)

        if len(self.features) > 0:
            character = character + "\n<b>Features:</b> " + self.features

        if len(self.style) > 0:
            character = character + "\n<b>Style:</b> " + self.style

        if self.magical_items:
            character = character + "\n<b>Possible Magical Items:</b> " + formatItems(self.magical_items) + ";"

        character = character.split("\n")
        #print(self.armor)
        #print(self.weapons)
        #print(self.gear)
        return character
