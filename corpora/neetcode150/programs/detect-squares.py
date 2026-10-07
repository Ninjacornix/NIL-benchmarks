import collections

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def detect_squares(data):
    lines=data.splitlines();by_x={};counts=collections.Counter();out=[]
    for line in lines[1:1+int(lines[0])]:
        op,x,y=line.split();x,y=int(x),int(y)
        if op==b'+':counts[x,y]+=1;by_x.setdefault(x,set()).add(y)
        else:
            total=0
            for y2 in by_x.get(x,set()):
                if y2==y:continue
                d=y2-y
                for x2 in (x-d,x+d):total+=counts[x,y2]*counts[x2,y]*counts[x2,y2]
            out.append(total)
    return rows([x] for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = detect_squares(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
