import collections

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def task_scheduler(data):
    k,text=data.split(b'\n',1);k=int(k);counts=collections.Counter(text)
    if not text:return scalar(0)
    peak=max(counts.values());return scalar(max(len(text),(peak-1)*(k+1)+sum(x==peak for x in counts.values())))

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = task_scheduler(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
