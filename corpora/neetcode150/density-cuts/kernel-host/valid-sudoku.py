def kernel(a):
    groups = [a[r * 9:(r + 1) * 9] for r in range(9)]
    groups += [a[c::9] for c in range(9)]
    groups += [[a[(r + i) * 9 + c + j] for i in range(3) for j in range(3)] for r in range(0, 9, 3) for c in range(0, 9, 3)]
    return all((len([x for x in g if x]) == len({x for x in g if x}) for g in groups))

def solve(data):
    a=list(map(int, data.split()))
    result=kernel(a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
