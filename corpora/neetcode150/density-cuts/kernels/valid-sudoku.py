def kernel(a):
    groups = [a[r * 9:(r + 1) * 9] for r in range(9)]
    groups += [a[c::9] for c in range(9)]
    groups += [[a[(r + i) * 9 + c + j] for i in range(3) for j in range(3)] for r in range(0, 9, 3) for c in range(0, 9, 3)]
    return all((len([x for x in g if x]) == len({x for x in g if x}) for g in groups))
