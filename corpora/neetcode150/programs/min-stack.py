def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def min_stack(data):
    lines=data.splitlines();stack=[];out=[]
    for line in lines[1:1+int(lines[0])]:
        words=line.split();op=words[0]
        if op==b'push':
            x=int(words[1]);stack.append((x,min(x,stack[-1][1]) if stack else x))
        elif op==b'pop':stack.pop()
        elif op==b'min':out.append(stack[-1][1])
        else:out.append(stack[-1][0])
    return rows([x] for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = min_stack(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
