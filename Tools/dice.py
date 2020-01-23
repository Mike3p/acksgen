import random
import re

def roll(dicecode):
	if isinstance(dicecode, int):
		return dicecode
	try:
			#a = re.split('d|-|\+', dicecode)
			a = re.split('[d\-+*]', dicecode)
			#print(a)
			number = int(a[0])
			die = int(a[1])
			modifier = 0
			result = 0

			if "-" in dicecode:
				modifier = int(a[2])
				for i in range(number):
					result = result + random.randint(1, die)
				return result - modifier
			if "+" in dicecode:
				modifier = int(a[2])
				for i in range(number):
					result = result + random.randint(1, die)
				return result + modifier
			if "*" in dicecode:
				modifier = int(a[2])
				for i in range(number):
					result = result + random.randint(1, die)
				return result * modifier
			else:
				for i in range(number):
					result = result + random.randint(1, die)
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

