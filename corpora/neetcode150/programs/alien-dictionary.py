import heapq

def alien_dictionary(data):
    lines=data.splitlines();words=lines[1:1+int(lines[0])];adj={x:set() for w in words for x in w};degree={x:0 for x in adj}
    for a,b in zip(words,words[1:]):
        for x,y in zip(a,b):
            if x!=y:
                if y not in adj[x]:adj[x].add(y);degree[y]+=1
                break
        else:
            if len(a)>len(b):return b'-1\n'
    heap=[x for x in adj if degree[x]==0];heapq.heapify(heap);out=[]
    while heap:
        u=heapq.heappop(heap);out.append(u)
        for v in adj[u]:
            degree[v]-=1
            if not degree[v]:heapq.heappush(heap,v)
    return (bytes(out) if len(out)==len(adj) else b'-1')+b'\n'

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = alien_dictionary(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
