import random
import re
import operator

def highest_x_of_y(number: int, rolls: int, dicecode: str):
	highest = []
	for i in range(rolls):
		highest.append(roll(dicecode))

	highest.sort(reverse=True)
	return highest[0:number]



def roll(dicecode: str):
	def calculate(input):
		ans = 0
		op = operator.add
		for item in input:

			if isInt(item):
				ans = op(ans,item)
			else:
				op = item
		return ans

	def isInt(n: str):
		try:
			int(n)
			return True
		except:
			return False
	rollelements = re.findall('\d+d\d+|[\+\-\*]|\d', dicecode)
	rollformatted = []
	ops = {"+": operator.add, "-": operator.sub, "*": operator.mul}
	for e in rollelements:
		if 'd' in e:
			r = 0
			nd = e.split('d')[0]
			dt = e.split('d')[1]
			for i in range(int(nd)):
				r += random.randint(1,int(dt))
			rollformatted.append(r)
		elif isInt(e):
			rollformatted.append(int(e))
		elif e in ops:
			rollformatted.append(ops[e])
	return calculate(rollformatted)

def get_ability_mod(a):
	if a >= 18: return 3
	elif a >= 16: return 2
	elif a >= 13: return 1
	elif a >= 9: return 0
	elif a >= 6: return -1
	elif a >= 4: return -2
	else: return -3

def get_ability_mod_str(a):
	mod = get_ability_mod(a)
	if mod >= 0:
		res = "+"+str(mod)
	else:
		res = str(mod)
	return res
