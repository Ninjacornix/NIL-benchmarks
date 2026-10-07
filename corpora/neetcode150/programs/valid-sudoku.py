def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def valid_sudoku(data):
    a = list(map(int, data.split()))
    groups = [a[r*9:(r+1)*9] for r in range(9)]
    groups += [a[c::9] for c in range(9)]
    groups += [[a[(r+i)*9+c+j] for i in range(3) for j in range(3)]
               for r in range(0,9,3) for c in range(0,9,3)]
    return scalar(all(len([x for x in g if x]) == len({x for x in g if x}) for g in groups))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = valid_sudoku(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
