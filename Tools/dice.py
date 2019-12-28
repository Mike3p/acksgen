import random
import re

def roll(dicecode):
	if isinstance(dicecode, int):
		return dicecode
	try:
			#a = re.split('d|-|\+', dicecode)
			a = re.split('[d\-+]', dicecode)
			number = int(a[0])
			die = int(a[1])
			modifier = 0
			if "-" in dicecode:
				modifier = -int(a[2])
			if "+" in dicecode:
				modifier = int(a[2])
			result = 0
			for i in range(number):
					result = result + random.randint(1, die)+modifier
			return result
	except:
		raise
		return ("not a valid die code")


def get_ability_mod(a):
	if a >= 18: return 3
	elif a >= 16: return 2
	elif a >= 13: return 1
	elif a >= 9: return 0
	elif a >= 6: return -1
	elif a >= 4: return -2
	else: return 3

