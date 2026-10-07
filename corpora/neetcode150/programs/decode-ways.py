def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def decode_ways(data):
    previous=current=1
    for i,x in enumerate(data):
        nxt=current if x!=48 else 0
        if i and 10<=int(data[i-1:i+1])<=26:nxt+=previous
        previous,current=current,nxt
    return scalar(current)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = decode_ways(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
