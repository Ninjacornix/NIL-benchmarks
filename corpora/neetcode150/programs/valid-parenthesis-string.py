def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def valid_parenthesis_string(data):
    lo=hi=0
    for x in data:
        lo=max(0,lo+(1 if x==40 else -1));hi+=-1 if x==41 else 1
        if hi<0:return scalar(False)
    return scalar(lo==0)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = valid_parenthesis_string(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
