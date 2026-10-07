def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def n_queens(data):
    n=int(data); out=[]
    def visit(path,columns,down,up):
        r=len(path)
        if r==n: out.append(path); return
        for c in range(n):
            if c not in columns and r-c not in down and r+c not in up:
                visit(path+[c],columns|{c},down|{r-c},up|{r+c})
    visit([],set(),set(),set())
    return rows(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = n_queens(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
