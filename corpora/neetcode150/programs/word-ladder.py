import collections

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def word_ladder(data):
    lines=data.splitlines();start,end=lines[:2];dictionary=set(lines[3:3+int(lines[2])])
    if end not in dictionary:return scalar(0)
    patterns={}
    for word in dictionary|{start}:
        for i in range(len(word)):patterns.setdefault(word[:i]+b'*'+word[i+1:],[]).append(word)
    queue=collections.deque([(start,1)]);seen={start}
    while queue:
        word,d=queue.popleft()
        if word==end:return scalar(d)
        for i in range(len(word)):
            key=word[:i]+b'*'+word[i+1:]
            for neighbour in patterns.pop(key,[]):
                if neighbour not in seen:seen.add(neighbour);queue.append((neighbour,d+1))
    return scalar(0)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = word_ladder(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
