def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def longest_substring_without_repeating_characters(data):
    last={}; left=best=0
    for i,x in enumerate(data):
        left=max(left,last.get(x,-1)+1); last[x]=i; best=max(best,i-left+1)
    return scalar(best)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = longest_substring_without_repeating_characters(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
