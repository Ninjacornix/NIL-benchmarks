import heapq

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def rows(values):
    return b''.join(row(x) for x in values)

def design_twitter(data):
    lines=data.splitlines();follow={};posts={};out=[];clock=0
    for line in lines[1:1+int(lines[0])]:
        p=line.split();u=int(p[1]);v=int(p[2]) if len(p)>2 else None
        if p[0]==b'post':posts.setdefault(u,[]).append((clock,v));clock+=1
        elif p[0]==b'follow':follow.setdefault(u,set()).add(v)
        elif p[0]==b'unfollow':follow.setdefault(u,set()).discard(v)
        else:
            heap=[]
            for who in follow.get(u,set())|{u}:
                items=posts.get(who,[])
                if items:heapq.heappush(heap,(-items[-1][0],who,len(items)-1))
            feed=[]
            while heap and len(feed)<10:
                _,who,j=heapq.heappop(heap);feed.append(posts[who][j][1]);j-=1
                if j>=0:heapq.heappush(heap,(-posts[who][j][0],who,j))
            out.append(feed)
    return rows(out)

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = design_twitter(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
