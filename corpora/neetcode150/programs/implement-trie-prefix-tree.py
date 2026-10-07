def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def implement_trie_prefix_tree(data):
    lines=data.split(b'\n'); count=int(lines[0]); children=[{}]; terminal=[False]; out=[]
    for line in lines[1:count+1]:
        op=line[:1]; word=line[2:]; node=0; present=True
        for x in word:
            if x not in children[node]:
                if op!=b'+': present=False; break
                children[node][x]=len(children); children.append({}); terminal.append(False)
            node=children[node][x]
        if op==b'+': terminal[node]=True
        else: out.append(int(present and (op==b'?' or terminal[node])))
    return rows([x] for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = implement_trie_prefix_tree(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
