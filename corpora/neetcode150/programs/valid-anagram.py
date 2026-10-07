import collections

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def valid_anagram(data):
    a,b=data.split(b'\n')[:2]; return scalar(collections.Counter(a)==collections.Counter(b))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = valid_anagram(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
