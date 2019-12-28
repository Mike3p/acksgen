class Skill:

    def __init__(self, name, ctype, throw = 0, modifiedBy = '', statsModified = {}, progression = []):
        self.name = name
        self.ctype = ctype
        self.throw = throw
        self.skillLevel = 1
        self.modifiedBy = modifiedBy
        self.statsModified = statsModified
        self.ranks = 0
        self.progression = progression

    def __repr__(self):

        name = self.name
        output = name
        if self.skillLevel <= 1:
            levelOfAbility = ''
        else:
            levelOfAbility = " (" + str(self.skillLevel) + ")"

        throw = " (" + str(self.throw) + "+)"

        if self.ranks <= 1:
            rank = ''
        else:
            rank = " " + str(self.ranks)

        if self.ctype == "throwable":
            output = name + rank + throw
        if self.ctype == "misc":
            output = name + rank + levelOfAbility

        return output

    def __hash__(self):
        return hash((self.name))

    def __eq__(self, other):
        return (self.name) == (other.name)
