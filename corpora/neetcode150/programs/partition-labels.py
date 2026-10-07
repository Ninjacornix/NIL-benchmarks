def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def partition_labels(data):
    last={x:i for i,x in enumerate(data)};start=end=0;out=[]
    for i,x in enumerate(data):
        end=max(end,last[x])
        if i==end:out.append(i-start+1);start=i+1
    return row(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = partition_labels(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
