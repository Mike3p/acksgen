from skill import Skill


class Character:
    # spells, special abilities and equipment
    def __init__(self):
        # class and level
        self.cls: str = ""
        self.lvl: int = 0
        self.name: str = ""

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
        self.equipment = []

    def applyStatMod(self, stats, value):
        for i in stats.keys():
            try:
                setattr(self, i, getattr(self, i) + (value) * stats[i])
            except:
                try:
                    for ability in self.abilities:
                        print("i: " + i)
                        print("a: " + ability.name)
                        print(i == ability.name)
                        if i == ability.name:
                            print(str(ability.throw))
                            print(value)
                            ability.throw += value * stats[i]
                            print(str(ability.throw))
                except:
                    pass

    def applyModifications(self):

        for a in self.abilities:
            a.throw = a.throw - self.getModByString(a.modifiedBy) - \
                      sum(self.lvl >= i for i in a.progression)
            a.skillLevel += sum(self.lvl >= i for i in a.progression)

            self.applyStatMod(a.statsModified, a.skillLevel)

        for p in self.proficiencies.values():
            p.throw = p.throw - self.getModByString(p.modifiedBy) - \
                      sum(self.lvl >= i for i in p.progression) - (4 * (p.ranks - 1))
            a.skillLevel += sum(self.lvl >= i for i in a.progression)

            self.applyStatMod(p.statsModified, p.skillLevel)

    def getFormattedCharacter(self):
        abilities_formatted = ""
        for x in self.abilities:
            abilities_formatted += x.formatAbility() + ", "
        abilities_formatted = abilities_formatted[:-2]

        proficiencies_formatted = ""
        for x in self.proficiencies.values():
            proficiencies_formatted += x.formatAbility() + ", "
        proficiencies_formatted = proficiencies_formatted[:-2]

        character = "{}: {} {}: Str: {}, Dex: {}, Con: {}, Int: {}, Wis: {}, Cha {};\n" \
                    "MV {}, AC {}, HD {}, hp {}, SP {}+, INI {}, " \
                    "PP {}+, PD {}+, BB {}+, SW {}+, M {}+, AL {};\n" \
                    "Attacks: (Melee: {}+, +{} DMG; Missile: {}+, +{} DMG );\n" \
                    "Class Abilities: {};\n" \
                    "Proficiencies: {};\n" \
                    "Gear: {}\n"
        character = character.format(
            "Name", self.cls, self.lvl, self.strength, self.dexterity, self.constitution, self.intelligence,
            self.wisdom, self.charisma,
            self.mv, self.ac, self.hd, self.hp, self.sp, self.ini,
            self.saves[0], self.saves[1], self.saves[2], self.saves[3], self.saves[4], self.al,
            self.at, self.cdb, self.mat, self.mdb,
            abilities_formatted, proficiencies_formatted, self.equipment)
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
            return 3

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
        return "blergh"
