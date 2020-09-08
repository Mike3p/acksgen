from Tools.dice import roll

val = 0

cnt = 0
for i in range(10000):
    r = 0
    while r < 9:
        r = roll("3d6")
    val = val + r
    if r > 12: cnt = cnt+1


print(val/10000)
print(cnt/10000)

a = [1,2,3,4]
b = a[1:]
x = 'a'
if x:
    print("dsdsaadsdasdsa")
print("nope")