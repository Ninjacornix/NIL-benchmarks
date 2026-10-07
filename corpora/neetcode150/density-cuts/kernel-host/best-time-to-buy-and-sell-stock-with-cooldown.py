def kernel(a):
    hold = -10 ** 18
    sold = -10 ** 18
    rest = 0
    for price in a:
        hold, sold, rest = (max(hold, rest - price), hold + price, max(rest, sold))
    return max(rest, sold)

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
