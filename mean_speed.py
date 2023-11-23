l = [5, 10, 15, 25]

print(sum(l) / len(l))

t = l.pop(len(l) - 1)
last_mean = sum(l) / len(l)
print()
print('last_mean\t', last_mean)
print('len(l)\t\t', len(l))
print('t\t\t', t)
print('l\t\t', l)

print(last_mean + (1/(len(l)+1)) * (t - last_mean))
