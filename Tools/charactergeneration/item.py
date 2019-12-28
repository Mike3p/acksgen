class Item():

    def __init__(self, amount = 1, name = 'item', weight = 0, cost = 0):
        self.amount = amount
        self.name = name
        self.weight = weight
        self.cost = cost

    def __repr__(self):
        return self.name + (" [" + str(self.amount) + "]" if self.amount > 1 else '')

class Weapon(Item):

    def __init__(self, amount = 1, name = 'item', weight = 0, cost = 0, mod = {}, damage = '1d6', type = 'melee'):
        super(Weapon, self).__init__(amount, name, weight, cost)
        self.mod = mod
        self.type = type
        self.damage = damage

    def __repr__(self):
        return super(Weapon, self).__repr__() + " (" + str(self.damage) + ")"

class Armor(Item):

    def __init__(self, amount = 1, name = 'item', weight = 0, cost = 0, ac = 1):
        super(Armor, self).__init__(amount, name, weight, cost)
        self.ac = ac