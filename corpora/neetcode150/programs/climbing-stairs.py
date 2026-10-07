def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def climbing_stairs(data):
    n=int(data);a=b=1
    for _ in range(n):a,b=b,a+b
    return scalar(a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = climbing_stairs(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
