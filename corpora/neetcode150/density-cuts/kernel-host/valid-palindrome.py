def kernel(data):
    a = bytes((x + 32 if 65 <= x <= 90 else x for x in data if 48 <= x <= 57 or 65 <= x <= 90 or 97 <= x <= 122))
    return a == a[::-1]

def solve(data):
    result=kernel(data)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
