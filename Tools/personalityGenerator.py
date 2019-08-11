import copy
import argparse
from . import dice

def createPersonality():
		personality = {}
		personality[('honorable','treacherous')] = dice.roll("3d6")
		personality[('humble','proud')] = dice.roll("3d6")
		personality[('Kind','Spiteful')] = dice.roll("3d6")
		personality[('Temperate','Gluttonous')] = dice.roll("3d6")
		personality[('Chaste','Lustful')] = dice.roll("3d6")
		personality[('Patient','Wrathful')] = dice.roll("3d6")
		personality[('Generous','Avaricious')] = dice.roll("3d6")
		personality[('Determined','Slothful')] = dice.roll("3d6")

		
		print(personality)