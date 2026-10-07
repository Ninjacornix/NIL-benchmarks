def kernel(a):
    carry = 1
    for i in range(len(a) - 1, -1, -1):
        a[i], carry = ((a[i] + carry) % 10, (a[i] + carry) // 10)
    return ([1] if carry else []) + a

def solve(data):
    a=list(map(int, data.split()))[1:]
    result=kernel(a)
    return (' '.join(map(str,result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
