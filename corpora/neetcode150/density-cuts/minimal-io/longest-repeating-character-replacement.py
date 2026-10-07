def kernel(k, line):
    counts = [0] * 26
    left = best = peak = 0
    for i, x in enumerate(line):
        counts[x - 65] += 1
        peak = max(peak, counts[x - 65])
        if i - left + 1 - peak > k:
            counts[line[left] - 65] -= 1
            left += 1
        best = max(best, i - left + 1)
    return best

def solve(data):
    k,line=data.split(b'\n',1)
    k=int(k)
    result=kernel(k,line)
    return (str(int(result))+'\n').encode()

if __name__ == '__main__':
    import sys
    from pathlib import Path
    result=solve(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(result)
    print(len(result))
