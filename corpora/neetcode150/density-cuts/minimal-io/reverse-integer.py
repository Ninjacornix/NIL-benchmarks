def kernel(a):
    out = []
    for value in a:
        negative = value < 0
        reversed_value = int(str(abs(value))[::-1])
        reversed_value = -reversed_value if negative else reversed_value
        out.append(reversed_value if -2 ** 31 <= reversed_value < 2 ** 31 else 0)
    return out

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
