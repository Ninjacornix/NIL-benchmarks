import collections

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def permutation_in_string(data):
    pattern,text=data.split(b'\n')[:2];counts=collections.Counter(pattern);window=collections.Counter()
    if not pattern:return scalar(True)
    for i,x in enumerate(text):
        window[x]+=1
        if i>=len(pattern):
            old=text[i-len(pattern)];window[old]-=1
            if not window[old]:del window[old]
        if window==counts:return scalar(True)
    return scalar(False)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = permutation_in_string(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
