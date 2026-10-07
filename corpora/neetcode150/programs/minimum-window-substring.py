import collections

def minimum_window_substring(data):
    text,pattern=data.split(b'\n')[:2]
    if not pattern:return b'\n'
    need=collections.Counter(pattern);missing=len(pattern);l=0;best=None
    for r,x in enumerate(text):
        if need[x]>0:missing-=1
        need[x]-=1
        while missing==0:
            if best is None or r-l+1<best[1]-best[0]:best=(l,r+1)
            old=text[l];need[old]+=1;l+=1
            if need[old]>0:missing+=1
    return (text[best[0]:best[1]] if best else b'')+b'\n'

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = minimum_window_substring(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
