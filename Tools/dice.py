import random
def roll(dicecode):
		try:
				a = dicecode.split("d")
				number = int(a[0])
				die = int(a[1])
				result = 0
				for i in range(number):
						result = result + random.randint(1, die)
				return result
		except:
				return ("not a valid die code")