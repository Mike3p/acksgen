from ..charactergeneration.personalityGenerator import create_personality_string
import math
import pickle

class Character:
    # spells, special abilities and equipment
    def __init__(self):
        # class, level, name, sex and ethnicity
        self.cls: str = ""
        self.lvl: int = 0
        self.name: str = "Name"
        self.path: str = ""
        self.ethnicity = "ethnicity"
        self.sex = "none"

        # personality and looks
        self.personality = ''
        self.build = 'Average'
        self.hairc = 'Black'
        self.hairt = 'Straight'
        self.eyec = 'Brown'
        self.features = []
        self.style = []
        self.descriptionString = ""
        self.styleString = ""
        self.featureString = ""
        self.personalityString = ""

        # core abilities
        self.strength: int = 0
        self.dexterity: int = 0
        self.constitution: int = 0
        self.intelligence: int = 0
        self.wisdom: int = 0
        self.charisma: int = 0

        # traits
        self.mv: int = 0
        self.ac: int = 0
        self.hd: str = ""
        self.hp: int = 0
        self.sp: int = 0
        self.ini: int = 0
        self.al: str = ""
        self.enc: int = 0

        # saves
        self.saves: [int] = []

        # attack and spell throws
        self.at: int = 0
        self.mat: int = 0
        self.ct: int = 0
        self.cdb: int = 0
        self.mdb: int = 0

        self.abilities = []
        self.proficiencies = {}
        self.spells = {}
        self.weapons =[]
        self.armor = []
        self.gear = []

    def applyModifications(self):

        def applyStatMod(stats, value):
            for i in stats.keys():
                try:
                    setattr(self, i, getattr(self, i) + (value) * stats[i])
                except:
                    try:
                        for ability in self.abilities:
                            if i == ability.name:
                                ability.throw += value * stats[i]
                    except:
                        pass

        def getMovementRate(weight):
            move = 120
            if weight > 35:
                move += -30
            if weight > 53:
                move += -30
            if weight > 65:
                move += -30
            if weight > 120 + self.strength*6:
                move += -30
            return move

        for a in self.abilities:
            a.throw = a.throw - self.getModByString(a.modifiedBy) - \
                      sum(self.lvl >= i for i in a.progression)
            a.skillLevel += sum(self.lvl >= i for i in a.progression)

            applyStatMod(a.statsModified, a.skillLevel)

        for p in self.proficiencies.values():
            p.throw = p.throw - self.getModByString(p.modifiedBy) - \
                      sum(self.lvl >= i for i in p.progression) - (4 * (p.ranks - 1))
            p.skillLevel += sum(self.lvl >= i for i in p.progression)

            applyStatMod(p.statsModified, p.skillLevel)

        for armr in self.armor:
            self.ac += armr.ac

        weight = 0
        for i in self.weapons:
            weight += i.weight
        for i in self.armor:
            weight += i.weight
        for i in self.gear:
            weight += i.weight

        self.mv = getMovementRate(weight)
        self.enc = weight

    def formatSpells(self):
        output = ""
        for i in self.spells:
            output = output + "L"+str(i)+": ("
            for j in self.spells.get(i):
                output += j + ", "
            output = output[:-2] + "); "
        output = output[:-2]
        return output

    def formatItems(self, items):
        output = ''
        for i in items:
            output += str(i)+ ", "
        output = output[:-2]
        if output == '':
            output = 'None'
        return output

    def formatSkills(self, skills):
        output = ""
        for x in skills:
            output += str(x) + ", "
        output = output[:-2]
        return output

    def getFormattedCharacter(self):

        abilities_formatted = self.formatSkills(self.abilities)

        proficiencies_formatted = self.formatSkills(self.proficiencies.values())

        spells_formatted = self.formatSpells()

        weapons_formatted = self.formatItems(self.weapons)
        armor_formatted = self.formatItems(self.armor)
        gear_formatted = self.formatItems(self.gear)

        melee_modifier = ("+"+str(self.cdb) if self.cdb >= 0 else str(self.cdb))
        missile_modifier = ("+" + str(self.mdb) if self.mdb >= 0 else str(self.mdb))

        encumbrance_formatted = "("+str(math.floor(self.enc / 6)) + "s, " + str(self.enc % 6) +"i)"

        pathString = (" ("+ self.path.capitalize() +") " if self.path else ' ')

        character = "<b>{}:</b> {}{}{}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha: {};\n" \
                    "<b>MV</b> {}, <b>AC</b> {}, <b>HD</b> {}, <b>hp</b> {}, <b>SP</b> {}+, <b>INI</b> {}, " \
                    "<b>PP</b> {}+, <b>PD</b> {}+, <b>BB</b> {}+, <b>SW</b> {}+, <b>M</b> {}+, <b>AL</b> {};\n" \
                    "<b>Attacks:</b> (<b>Melee:</b> {}+, {} dmg; <b>Missile:</b> {}+, {} dmg);\n" \
                    "<b>Weapons:</b> {}. " \
                    "<b>Armor:</b> {};\n" \
                    "<b>Class Abilities:</b> {};\n" \
                    "<b>Proficiencies:</b> {};\n" \
                    "<b>Equipment:</b> {}. {};"
        character = character.format(
            self.name, self.cls.capitalize(), pathString,self.lvl,
            self.strength, self.dexterity, self.constitution, self.intelligence, self.wisdom, self.charisma,
            self.mv, self.ac, self.hd, self.hp, self.sp, self.ini,
            self.saves[0], self.saves[1], self.saves[2], self.saves[3], self.saves[4], self.al,
            self.at, melee_modifier, self.mat, missile_modifier,
            weapons_formatted, armor_formatted,
            abilities_formatted, proficiencies_formatted,
            gear_formatted, encumbrance_formatted)

        if len(self.spells.keys()) > 0:
            spellstring = "\n<b>Spells</b>: {};"
            spellstring = spellstring.format(spells_formatted)
            character = character + spellstring

        perString = create_personality_string()
        self.personalityString = perString
        character = character + "\n" + "<b>Personality:</b> " + perString

        description = "\n<b>Desc:</b> {} {} {} with {} hair of {} texture and {} eyes;"
        description = description.format(self.build, self.sex, self.ethnicity.capitalize(), self.hairc, self.hairt, self.eyec)
        self.descriptionString = description.split("</b>")[1]
        character = character + description

        if len(self.features) > 0:
            features = "\n<b>Notable Features:</b>"
            for f in self.features:
                features = features + " " + f + ", "
            features = features[:-2] + ";"
            self.featureString = features.split("</b>")[1]
            character = character + features

        if len(self.style) > 0:
            style = "\n<b>Style:</b>"
            for s in self.style:
                if self.sex == 'male':
                    s = s.replace('[GENDERPOSS]', 'his')
                    s = s.replace('[GENDERPERS]', 'he')
                if self.sex == 'female':
                    s = s.replace('[GENDERPOSS]', 'her')
                    s = s.replace('[GENDERPERS]', 'she')
                style = style + " " + s.capitalize() + ". "
                self.styleString = style.split("</b>")[1]
            character = character + style

        character = character.split("\n")



        return character

    def getFormattedProficiencies(self):
        # format proficiencies for output
        proficiencies_formatted = ""
        for x in self.proficiencies:
            proficiencies_formatted += x
            if self.proficiencies[x] > 1:
                proficiencies_formatted += " " + str(self.proficiencies[x])
            proficiencies_formatted += ", "
        proficiencies_formatted = proficiencies_formatted[:-2]
        return proficiencies_formatted

    @staticmethod
    def getMod(stat: int):
        if stat >= 18:
            return 3
        elif stat >= 16:
            return 2
        elif stat >= 13:
            return 1
        elif stat >= 9:
            return 0
        elif stat >= 6:
            return -1
        elif stat >= 4:
            return -2
        else:
            return -3

    def getModByString(self, abilityName):
        try:
            modifier = self.getMod(getattr(self, abilityName))
        except AttributeError:
            modifier = 0
        return modifier

    def getStrMod(self):
        return self.getMod(self.strength)

    def getDexMod(self):
        return self.getMod(self.dexterity)

    def getConMod(self):
        return self.getMod(self.constitution)

    def getIntMod(self):
        return self.getMod(self.intelligence)

    def getWisMod(self):
        return self.getMod(self.wisdom)

    def getChaMod(self):
        return self.getMod(self.charisma)

    def __str__(self):
        return self.getFormattedCharacter()
