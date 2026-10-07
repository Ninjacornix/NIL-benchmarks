def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def design_add_and_search_words_data_structure(data):
    lines=data.splitlines();trie={};out=[]
    for line in lines[1:1+int(lines[0])]:
        op,word=line[:1],line[2:]
        if op==b'+':
            node=trie
            for x in word:node=node.setdefault(x,{})
            node[-1]=True
        else:
            frontier=[trie]
            for x in word:frontier=[child for node in frontier for k,child in node.items() if k!=-1 and (x==46 or x==k)]
            out.append(any(-1 in node for node in frontier))
    return rows([int(x)] for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = design_add_and_search_words_data_structure(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
