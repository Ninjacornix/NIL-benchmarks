import bisect

def time_based_key_value_store(data):
    lines=data.splitlines();records={};out=[]
    for line in lines[1:1+int(lines[0])]:
        p=line.split();key=p[1];t=int(p[2])
        if p[0]==b'set':records.setdefault(key,[]).append((t,p[3]))
        else:
            entries=records.get(key,[]);i=bisect.bisect_right(entries,(t,b'\xff'))-1;out.append(entries[i][1] if i>=0 else b'')
    return b''.join(x+b'\n' for x in out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = time_based_key_value_store(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
