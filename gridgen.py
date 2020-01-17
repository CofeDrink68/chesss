a = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]

for x in range(8):
    for y in range(8):
        print(a[y]+str(8-x), end=" ")
    print("\n")