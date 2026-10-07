def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def word_break(data):
    lines=data.splitlines();text=lines[0];trie={}
    for word in lines[2:2+int(lines[1])]:
        node=trie
        for x in word:node=node.setdefault(x,{})
        node[-1]=True
    dp=[False]*(len(text)+1);dp[0]=True
    for i in range(len(text)):
        if not dp[i]:continue
        node=trie
        for j in range(i,len(text)):
            if text[j] not in node:break
            node=node[text[j]]
            if -1 in node:dp[j+1]=True
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = word_break(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
