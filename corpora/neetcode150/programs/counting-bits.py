def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def counting_bits(data):
    n=int(data);a=[0]*(n+1)
    for i in range(1,n+1):a[i]=a[i//2]+i%2
    return row(a)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = counting_bits(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
