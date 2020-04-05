import copy
import argparse
from ..dice import roll, get_ability_mod


def create_personality():
    personality_factors = {('Honorable', 'Treacherous'): roll("3d6"), ('Humble', 'Proud'): roll("3d6"),
                           ('Kind', 'Spiteful'): roll("3d6"), ('Moderate', 'Gluttonous'): roll("3d6"),
                           ('Chaste', 'Lustful'): roll("3d6"), ('Patient', 'Wrathful'): roll("3d6"),
                           ('Determined', 'Slothful'): roll("3d6"), ('Brave', 'Cowardly'): roll("3d6"),
                           ('Humorous', 'Serious'): roll("3d6")}
    personality = {}
    for k in personality_factors.keys():
        m = get_ability_mod(personality_factors[k])
        personality[k] = m

    return personality


def create_personality_string():
    pers = create_personality()
    p = {}
    for k in pers:
        if pers[k] > 0:
            p[k[0]] = abs(pers[k])
        if pers[k] < 0:
            p[k[1]] = abs(pers[k])

    s = ""
    for i in p:
        s = s + i + ": " + str(abs(p[i])) + ", "
    if s:
        s = s[:-2]
        s = s + ";"
    if s == "":
        s = "Average"
    return s
