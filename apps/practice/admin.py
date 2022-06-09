a = {'a': 0, 'b': 0}
c = a.copy()
print(a, c)

d = {'a': 10, 'd': 12}

a.update(d)

print(a, c)
