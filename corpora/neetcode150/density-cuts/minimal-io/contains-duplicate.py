def kernel(a):
    return len(set(a)) != len(a)

def solve(data):
    a=list(map(int, data.split()))[1:]
    result=kernel(a)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
