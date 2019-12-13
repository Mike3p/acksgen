from dataclasses import dataclass

@dataclass
class Character:
    #class and level
    cclass: str
    level: int

    #core abilities
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    #traits
    mv: int
    ac: int
    hd: str
    hp: int
    sp: int
    ini: int
    sv: str
    al: str

    #saves
    pd: int
    pp: int
    bb: int
    ma: int
    sw: int

    #attack and spell throws
    at: int
    mat: int
    ct: int
    cdb: int
    mdb: int

    #spells, special abilities and equipment
    abilities: dict
    proficiencies: dict
    spells: dict
    equipment: list

    def getFormattedAbilities(self):
        for x in self.abilities.keys():
            abilities_formatted += x
            if self.abilities > 1:
                abilities_formatted += " " + str(self.abilities[x])
            abilities_formatted += ", "
        abilities_formatted = abilities_formatted[:-2]
        return abilities_formatted

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

    def __str__(self):
        return "blergh"
