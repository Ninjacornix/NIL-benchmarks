def word_search_ii(data):
    lines=data.split(b'\n'); r,c=map(int,lines[0].split()); board=[bytearray(x) for x in lines[1:1+r]]
    words=lines[r+2:r+2+int(lines[r+1])]; trie={}
    for word in words:
        node=trie
        for x in word: node=node.setdefault(x,{})
        node[-1]=word
    found=set()
    def visit(i,j,node):
        x=board[i][j]
        if x not in node: return
        child=node[x]
        if -1 in child: found.add(child[-1])
        board[i][j]=0
        for u,v in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
            if 0<=u<r and 0<=v<c and board[u][v]: visit(u,v,child)
        board[i][j]=x
    for i in range(r):
        for j in range(c): visit(i,j,trie)
    return b''.join(w+b'\n' for w in sorted(found))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = word_search_ii(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
