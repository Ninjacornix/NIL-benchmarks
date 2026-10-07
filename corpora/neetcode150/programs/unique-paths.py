def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def unique_paths(data):
    r,c=map(int,data.split());dp=[1]*c
    for _ in range(r-1):
        for j in range(1,c):dp[j]+=dp[j-1]
    return scalar(dp[-1])

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = unique_paths(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
