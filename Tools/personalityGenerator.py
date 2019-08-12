import copy
import argparse
from .dice import roll, get_ability_mod


def create_personality():
    personality_factors = {('Honorable', 'Treacherous'): roll("3d6"), ('Humble', 'Arrogant'): roll("3d6"),
                           ('Kind', 'Spiteful'): roll("3d6"), ('Moderate', 'Gluttonous'): roll("3d6"),
                           ('Chaste', 'Lustful'): roll("3d6"), ('Patient', 'Wrathful'): roll("3d6"),
                           ('Generous', 'Avaricious'): roll("3d6"),
                           ('Determined', 'Slothful'): roll("3d6")}
    personality = {}
    for k in personality_factors.keys():
        m = get_ability_mod(personality_factors[k])
        if m > 0:
            personality[k[0]] = abs(m)
        elif m < 0:
            personality[k[1]] = abs(m)

    return personality

def create_personality_string():

	p = create_personality()
	s = ""
	for i in p:
		s = s + i + ": " + str(p[i]) + ", "
	if s:
		s=s[:-2]
		s=s+";"
	if s == "":
		s= "Average"
	return s
