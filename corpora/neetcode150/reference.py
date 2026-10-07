"""Original reference algorithms. No upstream solution code imported."""
import collections
import heapq
import itertools
import bisect
import math

class Numbers:
    def __init__(self, data):
        self.it = iter(map(int, data.split()))
    def one(self):
        return next(self.it)
    def vector(self):
        return [self.one() for _ in range(self.one())]
    def rows(self, width):
        return [[self.one() for _ in range(width)] for _ in range(self.one())]

def row(values):
    return (' '.join(map(str, values))+'\n').encode()

def scalar(value):
    return row([int(value)])

def rows(values):
    return b''.join(row(x) for x in values)

def contains_duplicate(data):
    a = Numbers(data).vector()
    return scalar(len(set(a)) != len(a))

def valid_sudoku(data):
    a = list(map(int, data.split()))
    groups = [a[r*9:(r+1)*9] for r in range(9)]
    groups += [a[c::9] for c in range(9)]
    groups += [[a[(r+i)*9+c+j] for i in range(3) for j in range(3)]
               for r in range(0,9,3) for c in range(0,9,3)]
    return scalar(all(len([x for x in g if x]) == len({x for x in g if x}) for g in groups))

def three_sum(data):
    a = sorted(Numbers(data).vector()); out = []
    for i in range(len(a)-2):
        if i and a[i] == a[i-1]: continue
        l,r = i+1,len(a)-1
        while l<r:
            s = a[i]+a[l]+a[r]
            if s<0: l+=1
            elif s>0: r-=1
            else:
                out.append((a[i],a[l],a[r])); l+=1; r-=1
                while l<r and a[l]==a[l-1]: l+=1
                while l<r and a[r]==a[r+1]: r-=1
    return rows(out)

def valid_palindrome(data):
    a = bytes(x+32 if 65<=x<=90 else x for x in data if 48<=x<=57 or 65<=x<=90 or 97<=x<=122)
    return scalar(a==a[::-1])

def longest_substring_without_repeating_characters(data):
    last={}; left=best=0
    for i,x in enumerate(data):
        left=max(left,last.get(x,-1)+1); last[x]=i; best=max(best,i-left+1)
    return scalar(best)

def longest_repeating_character_replacement(data):
    k,line=data.split(b'\n',1); k=int(k); counts=[0]*26; left=best=peak=0
    for i,x in enumerate(line):
        counts[x-65]+=1; peak=max(peak,counts[x-65])
        if i-left+1-peak>k: counts[line[left]-65]-=1; left+=1
        best=max(best,i-left+1)
    return scalar(best)

def car_fleet(data):
    q=Numbers(data); target=q.one(); a=q.rows(2); a.sort(reverse=True)
    fleets=0; numerator=0; denominator=1
    for pos,speed in a:
        distance=target-pos
        if distance*denominator>numerator*speed:
            fleets+=1; numerator=distance; denominator=speed
    return scalar(fleets)

def generate_parentheses(data):
    n=int(data); out=[]
    def visit(s,opened,closed):
        if closed==n: out.append(s); return
        if opened<n: visit(s+'(',opened+1,closed)
        if closed<opened: visit(s+')',opened,closed+1)
    visit('',0,0)
    return ('\n'.join(out)+'\n').encode()

def median_of_two_sorted_arrays(data):
    q=Numbers(data); a=q.vector(); b=q.vector()
    if len(a)>len(b): a,b=b,a
    lo,hi=0,len(a); half=(len(a)+len(b)+1)//2
    while lo<=hi:
        i=(lo+hi)//2; j=half-i
        al=a[i-1] if i else -math.inf; ar=a[i] if i<len(a) else math.inf
        bl=b[j-1] if j else -math.inf; br=b[j] if j<len(b) else math.inf
        if al>br: hi=i-1
        elif bl>ar: lo=i+1
        else: return scalar(2*max(al,bl) if (len(a)+len(b))%2 else max(al,bl)+min(ar,br))
    raise AssertionError('sorted inputs')

def search_in_rotated_sorted_array(data):
    q=Numbers(data); a=q.vector(); target=q.one(); lo,hi=0,len(a)-1
    while lo<=hi:
        m=(lo+hi)//2
        if a[m]==target: return scalar(m)
        if a[lo]<=a[m]:
            if a[lo]<=target<a[m]: hi=m-1
            else: lo=m+1
        else:
            if a[m]<target<=a[hi]: lo=m+1
            else: hi=m-1
    return scalar(-1)

def reverse_linked_list(data):
    q=Numbers(data); n=q.one(); head=q.one(); a=[[q.one(),q.one()] for _ in range(n)]; out=[]
    while head!=-1: out.append(a[head][0]); head=a[head][1]
    return row(out[::-1])

def lru_cache(data):
    q=Numbers(data); cap=q.one(); count=q.one(); cache=collections.OrderedDict(); out=[]
    for _ in range(count):
        op,key=q.one(),q.one()
        if op==0:
            val=q.one(); cache.pop(key,None)
            if cap: cache[key]=val
            while len(cache)>cap: cache.popitem(last=False)
        elif key in cache:
            val=cache.pop(key); cache[key]=val; out.append(val)
        else: out.append(-1)
    return rows([x] for x in out)

def tree(data):
    q=Numbers(data); n=q.one(); root=q.one(); a=[[q.one(),q.one(),q.one()] for _ in range(n)]
    return a,root

def balanced_binary_tree(data):
    a,root=tree(data); heights=[0]*len(a); stack=[(root,False)] if root!=-1 else []; okay=True
    while stack:
        i,ready=stack.pop()
        if not ready:
            stack.append((i,True))
            for child in a[i][1:]:
                if child!=-1: stack.append((child,False))
        else:
            lh=heights[a[i][1]] if a[i][1]!=-1 else 0
            rh=heights[a[i][2]] if a[i][2]!=-1 else 0
            okay &= abs(lh-rh)<=1; heights[i]=max(lh,rh)+1
    return scalar(okay)

def validate_binary_search_tree(data):
    a,root=tree(data); stack=[]; current=root; previous=None
    while current!=-1 or stack:
        while current!=-1: stack.append(current); current=a[current][1]
        current=stack.pop(); value=a[current][0]
        if previous is not None and value<=previous: return scalar(False)
        previous=value; current=a[current][2]
    return scalar(True)

def implement_trie_prefix_tree(data):
    lines=data.split(b'\n'); count=int(lines[0]); children=[{}]; terminal=[False]; out=[]
    for line in lines[1:count+1]:
        op=line[:1]; word=line[2:]; node=0; present=True
        for x in word:
            if x not in children[node]:
                if op!=b'+': present=False; break
                children[node][x]=len(children); children.append({}); terminal.append(False)
            node=children[node][x]
        if op==b'+': terminal[node]=True
        else: out.append(int(present and (op==b'?' or terminal[node])))
    return rows([x] for x in out)

def word_search_ii(data):
    lines=data.split(b'\n'); r,c=map(int,lines[0].split()); board=[bytearray(x) for x in lines[1:1+r]]
    words=lines[r+2:r+2+int(lines[r+1])]; trie={}
    for word in words:
        node=trie
        for x in word: node=node.setdefault(x,{})
        node[-1]=word
    found=set()
    def visit(i,j,node):
        x=board[i][j]
        if x not in node: return
        child=node[x]
        if -1 in child: found.add(child[-1])
        board[i][j]=0
        for u,v in ((i-1,j),(i+1,j),(i,j-1),(i,j+1)):
            if 0<=u<r and 0<=v<c and board[u][v]: visit(u,v,child)
        board[i][j]=x
    for i in range(r):
        for j in range(c): visit(i,j,trie)
    return b''.join(w+b'\n' for w in sorted(found))

def last_stone_weight(data):
    heap=[-x for x in Numbers(data).vector()]; heapq.heapify(heap)
    while len(heap)>1:
        a,b=-heapq.heappop(heap),-heapq.heappop(heap)
        if a!=b: heapq.heappush(heap,b-a)
    return scalar(-heap[0] if heap else 0)

def kth_largest_element_in_an_array(data):
    q=Numbers(data); a=q.vector(); k=q.one()
    return scalar(sorted(a)[-k])

def n_queens(data):
    n=int(data); out=[]
    def visit(path,columns,down,up):
        r=len(path)
        if r==n: out.append(path); return
        for c in range(n):
            if c not in columns and r-c not in down and r+c not in up:
                visit(path+[c],columns|{c},down|{r-c},up|{r+c})
    visit([],set(),set(),set())
    return rows(out)

def letter_combinations_of_a_phone_number(data):
    letters=[b'abc',b'def',b'ghi',b'jkl',b'mno',b'pqrs',b'tuv',b'wxyz']
    return b''.join(bytes(x)+b'\n' for x in itertools.product(*(letters[d-50] for d in data))) if data else b''

def graph(data,weighted=False):
    q=Numbers(data); n,m=q.one(),q.one(); extra=q.one() if weighted else None
    width=3 if weighted else 2; edges=[[q.one() for _ in range(width)] for _ in range(m)]
    return n,edges,extra

def topological(n,edges):
    adjacent=[[] for _ in range(n)]; degree=[0]*n
    for u,v in edges: adjacent[u].append(v); degree[v]+=1
    heap=[i for i in range(n) if degree[i]==0]; heapq.heapify(heap); out=[]
    while heap:
        u=heapq.heappop(heap); out.append(u)
        for v in adjacent[u]:
            degree[v]-=1
            if degree[v]==0: heapq.heappush(heap,v)
    return out if len(out)==n else None

def course_schedule(data):
    n,edges,_=graph(data)
    return scalar(topological(n,edges) is not None)

def course_schedule_ii(data):
    n,edges,_=graph(data); answer=topological(n,edges)
    return row([-1] if answer is None else answer)

def cheapest_flights_within_k_stops(data):
    q=Numbers(data); n,m,s,t,k=[q.one() for _ in range(5)]; edges=[[q.one() for _ in range(3)] for _ in range(m)]
    dist=[10**18]*n; dist[s]=0
    for _ in range(k+1):
        new=dist.copy()
        for u,v,w in edges: new[v]=min(new[v],dist[u]+w)
        dist=new
    return scalar(-1 if dist[t]==10**18 else dist[t])

def network_delay_time(data):
    n,edges,s=graph(data,True); adjacent=[[] for _ in range(n)]
    for u,v,w in edges: adjacent[u].append((v,w))
    dist=[10**18]*n; dist[s]=0; heap=[(0,s)]
    while heap:
        d,u=heapq.heappop(heap)
        if d!=dist[u]: continue
        for v,w in adjacent[u]:
            if d+w<dist[v]: dist[v]=d+w; heapq.heappush(heap,(d+w,v))
    return scalar(-1 if 10**18 in dist else max(dist,default=0))

def min_cost_climbing_stairs(data):
    a=Numbers(data).vector(); x=y=0
    for cost in a: x,y=y,cost+min(x,y)
    return scalar(min(x,y))

def coin_change(data):
    q=Numbers(data); coins=q.vector(); amount=q.one(); dp=[0]+[amount+1]*amount
    for i in range(1,amount+1):
        for c in coins:
            if c<=i: dp[i]=min(dp[i],dp[i-c]+1)
    return scalar(-1 if dp[-1]>amount else dp[-1])

def target_sum(data):
    q=Numbers(data); a=q.vector(); target=q.one(); total=sum(a); dp=[0]*(2*total+1); dp[total]=1
    for x in a:
        new=[0]*len(dp)
        for i,count in enumerate(dp):
            if count:
                new[i+x]+=count; new[i-x]+=count
        dp=new
    return scalar(dp[total+target] if -total<=target<=total else 0)

def best_time_to_buy_and_sell_stock_with_cooldown(data):
    a=Numbers(data).vector(); hold=-10**18; sold=-10**18; rest=0
    for price in a: hold,sold,rest=max(hold,rest-price),hold+price,max(rest,sold)
    return scalar(max(rest,sold))

def gas_station(data):
    q=Numbers(data); gas=q.vector(); costs=q.vector(); prefix=0; low=0; start=0
    for i,(g,c) in enumerate(zip(gas,costs)):
        prefix+=g-c
        if prefix<low: low=prefix; start=i+1
    return scalar(start if gas and prefix>=0 else -1)

def maximum_subarray(data):
    a=Numbers(data).vector(); running=best=a[0]
    for x in a[1:]: running=max(x,running+x); best=max(best,running)
    return scalar(best)

def meeting_rooms(data):
    a=sorted(Numbers(data).rows(2))
    return scalar(all(a[i-1][1]<=a[i][0] for i in range(1,len(a))))

def insert_interval(data):
    q=Numbers(data); a=q.rows(2); lo,hi=q.one(),q.one(); out=[]; inserted=False
    for x,y in a:
        if y<lo: out.append((x,y))
        elif x>hi:
            if not inserted: out.append((lo,hi)); inserted=True
            out.append((x,y))
        else: lo=min(lo,x); hi=max(hi,y)
    if not inserted: out.append((lo,hi))
    return rows(out)

def plus_one(data):
    a=Numbers(data).vector(); carry=1
    for i in range(len(a)-1,-1,-1): a[i],carry=(a[i]+carry)%10,(a[i]+carry)//10
    return row(([1] if carry else [])+a)

def spiral_matrix(data):
    q=Numbers(data); r,c=q.one(),q.one(); a=[[q.one() for _ in range(c)] for _ in range(r)]; out=[]
    top,left,bottom,right=0,0,r,c
    while top<bottom and left<right:
        out.extend(a[top][left:right]); top+=1
        out.extend(a[i][right-1] for i in range(top,bottom)); right-=1
        if top<bottom: out.extend(reversed(a[bottom-1][left:right])); bottom-=1
        if left<right: out.extend(a[i][left] for i in range(bottom-1,top-1,-1)); left+=1
    return row(out)

def single_number(data):
    result=0
    for value in Numbers(data).vector(): result^=value
    return scalar(result)

def reverse_integer(data):
    out=[]
    for value in Numbers(data).vector():
        negative=value<0; reversed_value=int(str(abs(value))[::-1]); reversed_value= -reversed_value if negative else reversed_value
        out.append(reversed_value if -(2**31)<=reversed_value<2**31 else 0)
    return row(out)

SOLVERS={name.replace('_','-'):value for name,value in list(globals().items()) if callable(value) and name not in {'Numbers','row','rows','scalar','tree','graph','topological'}}
SOLVERS['3sum']=three_sum

# Remaining suite algorithms, authored against the local contracts.
def valid_anagram(data):
    a,b=data.split(b'\n')[:2]; return scalar(collections.Counter(a)==collections.Counter(b))
def two_sum(data):
    q=Numbers(data);a=q.vector();target=q.one();seen={}
    for i,x in enumerate(a):
        if target-x in seen:return row([seen[target-x],i])
        seen[x]=i
    raise ValueError('unique pair required')
def group_anagrams(data):
    lines=data.split(b'\n');groups={}
    for w in lines[1:1+int(lines[0])]:groups.setdefault(bytes(sorted(w)),[]).append(w)
    return b''.join(b' '.join(sorted(groups[k]))+b'\n' for k in sorted(groups))
def top_k_frequent_elements(data):
    q=Numbers(data);counts=collections.Counter(q.vector());k=q.one();return row(sorted(counts,key=lambda x:(-counts[x],x))[:k])
def product_of_array_except_self(data):
    a=Numbers(data).vector();out=[];prod=1
    for x in a:out.append(prod);prod*=x
    prod=1
    for i in range(len(a)-1,-1,-1):out[i]*=prod;prod*=a[i]
    return row(out)
def encode_and_decode_strings(data):
    pos=data.index(b'\n')+1;count=int(data[:pos]);out=b''
    for _ in range(count):
        end=data.index(b'\n',pos);n=int(data[pos:end]);pos=end+1;value=data[pos:pos+n];pos+=n
        out+=str(n).encode()+b':'+value
    return out
def longest_consecutive_sequence(data):
    values=set(Numbers(data).vector());best=0
    for x in values:
        if x-1 not in values:
            end=x
            while end in values:end+=1
            best=max(best,end-x)
    return scalar(best)
def two_sum_ii_input_array_is_sorted(data):
    q=Numbers(data);a=q.vector();t=q.one();l,r=0,len(a)-1
    while l<r:
        s=a[l]+a[r]
        if s==t:return row([l,r])
        if s<t:l+=1
        else:r-=1
    raise ValueError('unique pair required')
def container_with_most_water(data):
    a=Numbers(data).vector();l,r,best=0,len(a)-1,0
    while l<r:
        best=max(best,(r-l)*min(a[l],a[r]))
        if a[l]<a[r]:l+=1
        else:r-=1
    return scalar(best)
def trapping_rain_water(data):
    a=Numbers(data).vector();l,r=0,len(a)-1;left=right=total=0
    while l<=r:
        if left<=right:left=max(left,a[l]);total+=left-a[l];l+=1
        else:right=max(right,a[r]);total+=right-a[r];r-=1
    return scalar(total)
def best_time_to_buy_and_sell_stock(data):
    low=10**18;best=0
    for x in Numbers(data).vector():low=min(low,x);best=max(best,x-low)
    return scalar(best)
def permutation_in_string(data):
    pattern,text=data.split(b'\n')[:2];counts=collections.Counter(pattern);window=collections.Counter()
    if not pattern:return scalar(True)
    for i,x in enumerate(text):
        window[x]+=1
        if i>=len(pattern):
            old=text[i-len(pattern)];window[old]-=1
            if not window[old]:del window[old]
        if window==counts:return scalar(True)
    return scalar(False)
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
def sliding_window_maximum(data):
    q=Numbers(data);a=q.vector();k=q.one();queue=collections.deque();out=[]
    for i,x in enumerate(a):
        while queue and queue[0]<=i-k:queue.popleft()
        while queue and a[queue[-1]]<=x:queue.pop()
        queue.append(i)
        if i>=k-1:out.append(a[queue[0]])
    return row(out)
def valid_parentheses(data):
    stack=[];pairs={41:40,93:91,125:123}
    for x in data:
        if x in pairs:
            if not stack or stack.pop()!=pairs[x]:return scalar(False)
        else:stack.append(x)
    return scalar(not stack)
def min_stack(data):
    lines=data.splitlines();stack=[];out=[]
    for line in lines[1:1+int(lines[0])]:
        words=line.split();op=words[0]
        if op==b'push':
            x=int(words[1]);stack.append((x,min(x,stack[-1][1]) if stack else x))
        elif op==b'pop':stack.pop()
        elif op==b'min':out.append(stack[-1][1])
        else:out.append(stack[-1][0])
    return rows([x] for x in out)
def evaluate_reverse_polish_notation(data):
    tokens=data.split()[1:];stack=[]
    for x in tokens:
        if x in (b'+',b'-',b'*',b'/'):
            b,a=stack.pop(),stack.pop()
            value=a+b if x==b'+' else a-b if x==b'-' else a*b if x==b'*' else (abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            stack.append(value)
        else:stack.append(int(x))
    return scalar(stack[-1])
def daily_temperatures(data):
    a=Numbers(data).vector();stack=[];out=[0]*len(a)
    for i,x in enumerate(a):
        while stack and a[stack[-1]]<x:
            j=stack.pop();out[j]=i-j
        stack.append(i)
    return row(out)
def largest_rectangle_in_histogram(data):
    a=Numbers(data).vector();stack=[];best=0
    for i,h in enumerate(a+[0]):
        start=i
        while stack and stack[-1][1]>h:
            start,height=stack.pop();best=max(best,height*(i-start))
        stack.append((start,h))
    return scalar(best)
def binary_search(data):
    q=Numbers(data);a=q.vector();t=q.one();i=bisect.bisect_left(a,t);return scalar(i if i<len(a) and a[i]==t else -1)
def search_a_2d_matrix(data):
    q=Numbers(data);r,c=q.one(),q.one();a=[q.one() for _ in range(r*c)];t=q.one();i=bisect.bisect_left(a,t);return scalar(i<len(a) and a[i]==t)
def koko_eating_bananas(data):
    q=Numbers(data);a=q.vector();h=q.one();lo,hi=1,max(a)
    while lo<hi:
        m=(lo+hi)//2
        if sum((x+m-1)//m for x in a)<=h:hi=m
        else:lo=m+1
    return scalar(lo)
def find_minimum_in_rotated_sorted_array(data):
    a=Numbers(data).vector();lo,hi=0,len(a)-1
    while lo<hi:
        m=(lo+hi)//2
        if a[m]>a[hi]:lo=m+1
        else:hi=m
    return scalar(a[lo])
def time_based_key_value_store(data):
    lines=data.splitlines();records={};out=[]
    for line in lines[1:1+int(lines[0])]:
        p=line.split();key=p[1];t=int(p[2])
        if p[0]==b'set':records.setdefault(key,[]).append((t,p[3]))
        else:
            entries=records.get(key,[]);i=bisect.bisect_right(entries,(t,b'\xff'))-1;out.append(entries[i][1] if i>=0 else b'')
    return b''.join(x+b'\n' for x in out)
def merge_two_sorted_lists(data):
    q=Numbers(data);a=q.vector();b=q.vector();out=[];i=j=0
    while i<len(a) or j<len(b):
        if j==len(b) or (i<len(a) and a[i]<=b[j]):out.append(a[i]);i+=1
        else:out.append(b[j]);j+=1
    return row(out)
def reorder_list(data):
    a=Numbers(data).vector();out=[];l,r=0,len(a)-1
    while l<=r:
        out.append(a[l]);l+=1
        if l<=r:out.append(a[r]);r-=1
    return row(out)
def remove_nth_node_from_end_of_list(data):
    q=Numbers(data);a=q.vector();k=q.one();del a[len(a)-k];return row(a)
def copy_list_with_random_pointer(data):
    q=Numbers(data);n,head=q.one(),q.one();a=[[q.one() for _ in range(3)] for _ in range(n)];order=[]
    while head!=-1:order.append(head);head=a[head][1]
    index={old:i for i,old in enumerate(order)};index[-1]=-1
    return rows([a[u][0],index[a[u][1]],index[a[u][2]]] for u in order)
def add_two_numbers(data):
    q=Numbers(data);a=q.vector();b=q.vector();out=[];carry=0
    for i in range(max(len(a),len(b))):
        x=(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0)+carry;out.append(x%10);carry=x//10
    if carry:out.append(carry)
    return row(out)
def linked_list_cycle(data):
    q=Numbers(data);n,head=q.one(),q.one();a=[[q.one(),q.one()] for _ in range(n)];slow=fast=head
    while fast!=-1 and a[fast][1]!=-1:
        slow=a[slow][1];fast=a[a[fast][1]][1]
        if slow==fast:return scalar(True)
    return scalar(False)
def find_the_duplicate_number(data):
    a=Numbers(data).vector();s=f=a[0]
    while True:
        s=a[s];f=a[a[f]]
        if s==f:break
    s=a[0]
    while s!=f:s=a[s];f=a[f]
    return scalar(s)
def merge_k_sorted_lists(data):
    q=Numbers(data);lists=[q.vector() for _ in range(q.one())];heap=[(a[0],i,0) for i,a in enumerate(lists) if a];heapq.heapify(heap);out=[]
    while heap:
        x,i,j=heapq.heappop(heap);out.append(x);j+=1
        if j<len(lists[i]):heapq.heappush(heap,(lists[i][j],i,j))
    return row(out)
def reverse_nodes_in_k_group(data):
    q=Numbers(data);a=q.vector();k=q.one()
    for i in range(0,len(a)-k+1,k):a[i:i+k]=reversed(a[i:i+k])
    return row(a)

def tree_from(q):
    n,root=q.one(),q.one();return [[q.one() for _ in range(3)] for _ in range(n)],root

def levels(a,root):
    queue=[root] if root!=-1 else [];out=[]
    while queue:
        out.append(queue);queue=[child for u in queue for child in a[u][1:] if child!=-1]
    return out

def invert_binary_tree(data):
    a,root=tree(data);return rows([v,r,l] for v,l,r in a)
def maximum_depth_of_binary_tree(data):
    a,root=tree(data);return scalar(len(levels(a,root)))
def postorder(a,root):
    stack=[(root,False)] if root!=-1 else [];out=[]
    while stack:
        u,done=stack.pop()
        if done:out.append(u)
        else:
            stack.append((u,True));stack.extend((v,False) for v in a[u][1:] if v!=-1)
    return out
def diameter_of_binary_tree(data):
    a,root=tree(data);heights=[0]*len(a);best=0
    for u in postorder(a,root):
        l=heights[a[u][1]] if a[u][1]!=-1 else 0;r=heights[a[u][2]] if a[u][2]!=-1 else 0;best=max(best,l+r);heights[u]=max(l,r)+1
    return scalar(best)
def same_tree(data):
    q=Numbers(data);a,r=tree_from(q);b,s=tree_from(q);stack=[(r,s)]
    while stack:
        u,v=stack.pop()
        if u==-1 or v==-1:
            if u!=v:return scalar(False)
        elif a[u][0]!=b[v][0]:return scalar(False)
        else:stack.extend(zip(a[u][1:],b[v][1:]))
    return scalar(True)
def tree_tokens(a,root):
    stack=[root];out=[]
    while stack:
        u=stack.pop()
        if u==-1:out.append(None)
        else:out.append(a[u][0]);stack.extend(reversed(a[u][1:]))
    return out

def subtree_of_another_tree(data):
    q=Numbers(data);a,r=tree_from(q);b,s=tree_from(q)
    if s==-1:return scalar(True)
    text=tree_tokens(a,r);pattern=tree_tokens(b,s);prefix=[0]*len(pattern);j=0
    for i in range(1,len(pattern)):
        while j and pattern[i]!=pattern[j]:j=prefix[j-1]
        if pattern[i]==pattern[j]:j+=1
        prefix[i]=j
    j=0
    for x in text:
        while j and x!=pattern[j]:j=prefix[j-1]
        if x==pattern[j]:j+=1
        if j==len(pattern):return scalar(True)
    return scalar(False)
def lowest_common_ancestor_of_a_binary_search_tree(data):
    q=Numbers(data);a,u=tree_from(q);p,s=q.one(),q.one();lo,hi=sorted([a[p][0],a[s][0]])
    while True:
        if a[u][0]<lo:u=a[u][2]
        elif a[u][0]>hi:u=a[u][1]
        else:return scalar(u)
def binary_tree_level_order_traversal(data):
    a,r=tree(data);return rows([a[u][0] for u in level] for level in levels(a,r))
def binary_tree_right_side_view(data):
    a,r=tree(data);return row(a[level[-1]][0] for level in levels(a,r))
def count_good_nodes_in_binary_tree(data):
    a,r=tree(data);stack=[(r,-10**18)] if r!=-1 else [];count=0
    while stack:
        u,peak=stack.pop();count+=a[u][0]>=peak;stack.extend((v,max(peak,a[u][0])) for v in a[u][1:] if v!=-1)
    return scalar(count)
def kth_smallest_element_in_a_bst(data):
    q=Numbers(data);a,u=tree_from(q);k=q.one();stack=[]
    while True:
        while u!=-1:stack.append(u);u=a[u][1]
        u=stack.pop();k-=1
        if not k:return scalar(a[u][0])
        u=a[u][2]
def construct_binary_tree_from_preorder_and_inorder_traversal(data):
    q=Numbers(data);pre=q.vector();ino=q.vector();a=[[x,-1,-1] for x in pre];stack=[];j=0
    for i,x in enumerate(pre):
        if stack:
            if a[stack[-1]][0]!=ino[j]:a[stack[-1]][1]=i
            else:
                while stack and a[stack[-1]][0]==ino[j]:parent=stack.pop();j+=1
                a[parent][2]=i
        stack.append(i)
    return rows(a)
def binary_tree_maximum_path_sum(data):
    a,r=tree(data);gain=[0]*len(a);best=-10**18
    for u in postorder(a,r):
        l=max(0,gain[a[u][1]]) if a[u][1]!=-1 else 0;rr=max(0,gain[a[u][2]]) if a[u][2]!=-1 else 0
        best=max(best,a[u][0]+l+rr);gain[u]=a[u][0]+max(l,rr)
    return scalar(best)
def serialize_and_deserialize_binary_tree(data):
    a,r=tree(data);return (' '.join('#' if x is None else str(x) for x in tree_tokens(a,r))+'\n').encode()
def design_add_and_search_words_data_structure(data):
    lines=data.splitlines();trie={};out=[]
    for line in lines[1:1+int(lines[0])]:
        op,word=line[:1],line[2:]
        if op==b'+':
            node=trie
            for x in word:node=node.setdefault(x,{})
            node[-1]=True
        else:
            frontier=[trie]
            for x in word:frontier=[child for node in frontier for k,child in node.items() if k!=-1 and (x==46 or x==k)]
            out.append(any(-1 in node for node in frontier))
    return rows([int(x)] for x in out)
def kth_largest_element_in_a_stream(data):
    q=Numbers(data);k=q.one();a=q.vector();stream=q.vector();heap=sorted(a,reverse=True)[:k];heapq.heapify(heap);out=[]
    for x in stream:
        if len(heap)<k:heapq.heappush(heap,x)
        elif x>heap[0]:heapq.heapreplace(heap,x)
        out.append(heap[0])
    return row(out)
def k_closest_points_to_origin(data):
    q=Numbers(data);n,k=q.one(),q.one();a=[(q.one(),q.one()) for _ in range(n)];a.sort(key=lambda p:(p[0]**2+p[1]**2,p));return rows(a[:k])
def task_scheduler(data):
    k,text=data.split(b'\n',1);k=int(k);counts=collections.Counter(text)
    if not text:return scalar(0)
    peak=max(counts.values());return scalar(max(len(text),(peak-1)*(k+1)+sum(x==peak for x in counts.values())))
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
def find_median_from_data_stream(data):
    low=[];high=[];out=[]
    for x in Numbers(data).vector():
        heapq.heappush(low,-x);heapq.heappush(high,-heapq.heappop(low))
        if len(high)>len(low):heapq.heappush(low,-heapq.heappop(high))
        out.append(-2*low[0] if len(low)>len(high) else -low[0]+high[0])
    return row(out)
def subsets(data):
    a=sorted(Numbers(data).vector());out=[[]]
    for x in a:out += [s+[x] for s in out]
    return rows(sorted(out))
def subsets_ii(data):
    a=sorted(Numbers(data).vector());out=[[]];old=0
    for i,x in enumerate(a):
        start=old if i and a[i-1]==x else 0;old=len(out);out += [out[j]+[x] for j in range(start,old)]
    return rows(sorted(out))
def permutations(data):
    return rows(sorted(itertools.permutations(Numbers(data).vector())))
def combinations(data,reusable):
    q=Numbers(data);a=sorted(q.vector());target=q.one();out=[]
    def visit(i,left,path):
        if left==0:out.append(path);return
        for j in range(i,len(a)):
            if j>i and a[j]==a[j-1]:continue
            if a[j]>left:break
            visit(j if reusable else j+1,left-a[j],path+[a[j]])
    visit(0,target,[]);return rows(out)
def combination_sum(data):return combinations(data,True)
def combination_sum_ii(data):return combinations(data,False)
def word_search(data):
    lines=data.split(b'\n');r,c=map(int,lines[0].split());board=lines[1:1+r];word=lines[1+r];seen=set()
    def visit(i,j,k):
        if k==len(word):return True
        if not (0<=i<r and 0<=j<c) or (i,j) in seen or board[i][j]!=word[k]:return False
        seen.add((i,j));result=any(visit(u,v,k+1) for u,v in ((i+1,j),(i-1,j),(i,j-1),(i,j+1)));seen.remove((i,j));return result
    return scalar(not word or any(visit(i,j,0) for i in range(r) for j in range(c)))
def palindrome_partitioning(data):
    text=data.rstrip(b'\n');out=[]
    def visit(i,path):
        if i==len(text):out.append(b' '.join(path));return
        for j in range(i+1,len(text)+1):
            s=text[i:j]
            if s==s[::-1]:visit(j,path+[s])
    visit(0,[]);return b''.join(s+b'\n' for s in sorted(out))

def grid(data):
    q=Numbers(data);r,c=q.one(),q.one();return r,c,[q.one() for _ in range(r*c)]
def neighbours(u,r,c):
    i,j=divmod(u,c)
    if i:yield u-c
    if i+1<r:yield u+c
    if j:yield u-1
    if j+1<c:yield u+1

def island_sizes(data):
    r,c,a=grid(data);out=[]
    for start in range(len(a)):
        if a[start]!=1:continue
        a[start]=0;stack=[start];size=0
        while stack:
            u=stack.pop();size+=1
            for v in neighbours(u,r,c):
                if a[v]==1:a[v]=0;stack.append(v)
        out.append(size)
    return out

def number_of_islands(data):return scalar(len(island_sizes(data)))
def max_area_of_island(data):return scalar(max(island_sizes(data),default=0))
def pacific_atlantic_water_flow(data):
    r,c,a=grid(data)
    if not a:return b''
    def flood(starts):
        seen=set(starts);stack=list(seen)
        while stack:
            u=stack.pop()
            for v in neighbours(u,r,c):
                if v not in seen and a[v]>=a[u]:seen.add(v);stack.append(v)
        return seen
    first=flood(list(range(c))+list(range(0,r*c,c)));second=flood(list(range((r-1)*c,r*c))+list(range(c-1,r*c,c)))
    return rows(divmod(u,c) for u in sorted(first&second))
def surrounded_regions(data):
    r,c,a=grid(data);stack=[]
    for u in range(len(a)):
        i,j=divmod(u,c)
        if (i==0 or j==0 or i==r-1 or j==c-1) and a[u]==1:a[u]=2;stack.append(u)
    while stack:
        u=stack.pop()
        for v in neighbours(u,r,c):
            if a[v]==1:a[v]=2;stack.append(v)
    return row(1 if x==2 else 0 for x in a)
def rotting_oranges(data):
    r,c,a=grid(data);queue=collections.deque((i,0) for i,x in enumerate(a) if x==2);fresh=a.count(1);time=0
    while queue:
        u,time=queue.popleft()
        for v in neighbours(u,r,c):
            if a[v]==1:a[v]=2;fresh-=1;queue.append((v,time+1))
    return scalar(-1 if fresh else time)
def walls_and_gates(data):
    r,c,a=grid(data);dist=[-1 if x==-1 else 2147483647 for x in a];queue=collections.deque()
    for i,x in enumerate(a):
        if x==0:dist[i]=0;queue.append(i)
    while queue:
        u=queue.popleft()
        for v in neighbours(u,r,c):
            if dist[v]==2147483647:dist[v]=dist[u]+1;queue.append(v)
    return row(dist)
def clone_graph(data):
    q=Numbers(data);n,m=q.one(),q.one();adj=[set() for _ in range(n)]
    for _ in range(m):u,v=q.one(),q.one();adj[u].add(v);adj[v].add(u)
    start=q.one();seen=set();stack=[start] if start!=-1 else []
    while stack:
        u=stack.pop()
        if u in seen:continue
        seen.add(u);stack.extend(adj[u]-seen)
    return row(sorted(seen))+rows([u]+sorted(adj[u]) for u in sorted(seen))
def union_count(data,mode):
    n,edges,_=graph(data);parent=list(range(n));rank=[0]*n;count=n;last=None
    def root(u):
        while u!=parent[u]:parent[u]=parent[parent[u]];u=parent[u]
        return u
    for u,v in edges:
        a,b=root(u),root(v)
        if a==b:last=(u,v);continue
        if rank[a]<rank[b]:a,b=b,a
        parent[b]=a;count-=1
        if rank[a]==rank[b]:rank[a]+=1
    if mode=='redundant':return row(last)
    return scalar(count if mode=='components' else n>0 and count==1 and len(edges)==n-1)
def redundant_connection(data):return union_count(data,'redundant')
def number_of_connected_components_in_an_undirected_graph(data):return union_count(data,'components')
def graph_valid_tree(data):return union_count(data,'tree')
def word_ladder(data):
    lines=data.splitlines();start,end=lines[:2];dictionary=set(lines[3:3+int(lines[2])])
    if end not in dictionary:return scalar(0)
    patterns={}
    for word in dictionary|{start}:
        for i in range(len(word)):patterns.setdefault(word[:i]+b'*'+word[i+1:],[]).append(word)
    queue=collections.deque([(start,1)]);seen={start}
    while queue:
        word,d=queue.popleft()
        if word==end:return scalar(d)
        for i in range(len(word)):
            key=word[:i]+b'*'+word[i+1:]
            for neighbour in patterns.pop(key,[]):
                if neighbour not in seen:seen.add(neighbour);queue.append((neighbour,d+1))
    return scalar(0)
def reconstruct_itinerary(data):
    tokens=data.split();adj={}
    for i in range(int(tokens[0])):adj.setdefault(tokens[1+2*i],[]).append(tokens[2+2*i])
    for a in adj.values():a.sort(reverse=True)
    stack=[b'AAA'];out=[]
    while stack:
        a=adj.get(stack[-1],[])
        if a:stack.append(a.pop())
        else:out.append(stack.pop())
    return b' '.join(reversed(out))+b'\n'
def min_cost_to_connect_all_points(data):
    q=Numbers(data);a=q.rows(2);n=len(a);seen=[False]*n;dist=[10**18]*n;total=0
    if n:dist[0]=0
    for _ in range(n):
        u=min((i for i in range(n) if not seen[i]),key=lambda i:dist[i]);total+=dist[u];seen[u]=True
        for v in range(n):
            if not seen[v]:dist[v]=min(dist[v],abs(a[u][0]-a[v][0])+abs(a[u][1]-a[v][1]))
    return scalar(total)
def swim_in_rising_water(data):
    q=Numbers(data);n=q.one();a=[q.one() for _ in range(n*n)];dist=[10**18]*len(a);dist[0]=a[0];heap=[(a[0],0)]
    while heap:
        d,u=heapq.heappop(heap)
        if u==len(a)-1:return scalar(d)
        if d!=dist[u]:continue
        for v in neighbours(u,n,n):
            cost=max(d,a[v])
            if cost<dist[v]:dist[v]=cost;heapq.heappush(heap,(cost,v))
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

def climbing_stairs(data):
    n=int(data);a=b=1
    for _ in range(n):a,b=b,a+b
    return scalar(a)
def house_value(a):
    skip=take=0
    for x in a:skip,take=max(skip,take),skip+x
    return max(skip,take)
def house_robber(data):return scalar(house_value(Numbers(data).vector()))
def house_robber_ii(data):
    a=Numbers(data).vector();return scalar(a[0] if len(a)==1 else max(house_value(a[:-1]),house_value(a[1:])))
def palindrome_spans(text):
    for center in range(2*len(text)-1):
        l=center//2;r=l+center%2
        while l>=0 and r<len(text) and text[l]==text[r]:yield l,r+1;l-=1;r+=1

def longest_palindromic_substring(data):
    best=(0,0)
    for l,r in palindrome_spans(data):
        if r-l>best[1]-best[0] or (r-l==best[1]-best[0] and l<best[0]):best=(l,r)
    return data[best[0]:best[1]]+b'\n'
def palindromic_substrings(data):return scalar(sum(1 for _ in palindrome_spans(data)))
def decode_ways(data):
    previous=current=1
    for i,x in enumerate(data):
        nxt=current if x!=48 else 0
        if i and 10<=int(data[i-1:i+1])<=26:nxt+=previous
        previous,current=current,nxt
    return scalar(current)
def maximum_product_subarray(data):
    a=Numbers(data).vector();low=high=best=a[0]
    for x in a[1:]:low,high=min(x,low*x,high*x),max(x,low*x,high*x);best=max(best,high)
    return scalar(best)
def word_break(data):
    lines=data.splitlines();text=lines[0];trie={}
    for word in lines[2:2+int(lines[1])]:
        node=trie
        for x in word:node=node.setdefault(x,{})
        node[-1]=True
    dp=[False]*(len(text)+1);dp[0]=True
    for i in range(len(text)):
        if not dp[i]:continue
        node=trie
        for j in range(i,len(text)):
            if text[j] not in node:break
            node=node[text[j]]
            if -1 in node:dp[j+1]=True
    return scalar(dp[-1])
def longest_increasing_subsequence(data):
    tails=[]
    for x in Numbers(data).vector():
        i=bisect.bisect_left(tails,x)
        if i==len(tails):tails.append(x)
        else:tails[i]=x
    return scalar(len(tails))
def partition_equal_subset_sum(data):
    a=Numbers(data).vector();total=sum(a)
    if total%2:return scalar(False)
    target=total//2;dp=bytearray(target+1);dp[0]=1
    for x in a:
        for j in range(target,x-1,-1):dp[j]|=dp[j-x]
    return scalar(dp[target])
def unique_paths(data):
    r,c=map(int,data.split());dp=[1]*c
    for _ in range(r-1):
        for j in range(1,c):dp[j]+=dp[j-1]
    return scalar(dp[-1])
def longest_common_subsequence(data):
    a,b=data.split(b'\n')[:2];dp=[0]*(len(b)+1)
    for x in a:
        old=0
        for j,y in enumerate(b,1):prev=dp[j];dp[j]=old+1 if x==y else max(dp[j],dp[j-1]);old=prev
    return scalar(dp[-1])
def coin_change_ii(data):
    q=Numbers(data);coins=q.vector();target=q.one();dp=[0]*(target+1);dp[0]=1
    for c in coins:
        for j in range(c,target+1):dp[j]+=dp[j-c]
    return scalar(dp[-1])
def interleaving_string(data):
    a,b,c=data.split(b'\n')[:3]
    if len(a)+len(b)!=len(c):return scalar(False)
    dp=[False]*(len(b)+1);dp[0]=True
    for j in range(1,len(b)+1):dp[j]=dp[j-1] and b[j-1]==c[j-1]
    for i in range(1,len(a)+1):
        dp[0]=dp[0] and a[i-1]==c[i-1]
        for j in range(1,len(b)+1):dp[j]=(dp[j] and a[i-1]==c[i+j-1]) or (dp[j-1] and b[j-1]==c[i+j-1])
    return scalar(dp[-1])
def longest_increasing_path_in_a_matrix(data):
    r,c,a=grid(data);degree=[sum(a[v]<a[u] for v in neighbours(u,r,c)) for u in range(len(a))];front=[u for u in range(len(a)) if not degree[u]];length=0
    while front:
        length+=1;next_front=[]
        for u in front:
            for v in neighbours(u,r,c):
                if a[v]>a[u]:
                    degree[v]-=1
                    if not degree[v]:next_front.append(v)
        front=next_front
    return scalar(length)
def distinct_subsequences(data):
    a,b=data.split(b'\n')[:2];dp=[0]*(len(b)+1);dp[0]=1
    for x in a:
        for j in range(len(b),0,-1):
            if b[j-1]==x:dp[j]+=dp[j-1]
    return scalar(dp[-1])
def edit_distance(data):
    a,b=data.split(b'\n')[:2];dp=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        old=dp[0];dp[0]=i
        for j,y in enumerate(b,1):prev=dp[j];dp[j]=old if x==y else 1+min(old,dp[j],dp[j-1]);old=prev
    return scalar(dp[-1])
def burst_balloons(data):
    a=[1]+Numbers(data).vector()+[1];n=len(a);dp=[[0]*n for _ in range(n)]
    for width in range(2,n):
        for l in range(n-width):
            r=l+width;dp[l][r]=max((dp[l][k]+dp[k][r]+a[l]*a[k]*a[r] for k in range(l+1,r)),default=0)
    return scalar(dp[0][-1])
def regular_expression_matching(data):
    text,pattern=data.split(b'\n')[:2];m=len(pattern);dp=[False]*(m+1);dp[0]=True
    for j in range(2,m+1):
        if pattern[j-1]==42:dp[j]=dp[j-2]
    for x in text:
        previous=dp;dp=[False]*(m+1)
        for j in range(1,m+1):
            if pattern[j-1]==42:dp[j]=dp[j-2] or (previous[j] and pattern[j-2] in (46,x))
            else:dp[j]=previous[j-1] and pattern[j-1] in (46,x)
    return scalar(dp[-1])
def jump_game(data):
    a=Numbers(data).vector();reach=0
    for i,x in enumerate(a):
        if i>reach:return scalar(False)
        reach=max(reach,i+x)
    return scalar(bool(a))
def jump_game_ii(data):
    a=Numbers(data).vector();end=reach=count=0
    for i in range(len(a)-1):
        reach=max(reach,i+a[i])
        if i==end:count+=1;end=reach
    return scalar(count)
def hand_of_straights(data):
    q=Numbers(data);a=q.vector();size=q.one();counts=collections.Counter(a)
    if len(a)%size:return scalar(False)
    for x in sorted(counts):
        count=counts[x]
        if count:
            for y in range(x,x+size):
                if counts[y]<count:return scalar(False)
                counts[y]-=count
    return scalar(True)
def merge_triplets_to_form_target_triplet(data):
    q=Numbers(data);a=q.rows(3);target=[q.one() for _ in range(3)];best=[-10**18]*3
    for p in a:
        if all(x<=t for x,t in zip(p,target)):best=[max(x,y) for x,y in zip(best,p)]
    return scalar(best==target)
def partition_labels(data):
    last={x:i for i,x in enumerate(data)};start=end=0;out=[]
    for i,x in enumerate(data):
        end=max(end,last[x])
        if i==end:out.append(i-start+1);start=i+1
    return row(out)
def valid_parenthesis_string(data):
    lo=hi=0
    for x in data:
        lo=max(0,lo+(1 if x==40 else -1));hi+=-1 if x==41 else 1
        if hi<0:return scalar(False)
    return scalar(lo==0)
def merge_intervals(data):
    a=sorted(Numbers(data).rows(2));out=[]
    for x,y in a:
        if out and x<=out[-1][1]:out[-1][1]=max(out[-1][1],y)
        else:out.append([x,y])
    return rows(out)
def non_overlapping_intervals(data):
    a=sorted(Numbers(data).rows(2),key=lambda p:p[1]);end=-10**18;removed=0
    for x,y in a:
        if x<end:removed+=1
        else:end=y
    return scalar(removed)
def meeting_rooms_ii(data):
    a=Numbers(data).rows(2);events=sorted([(x,1) for x,y in a]+[(y,-1) for x,y in a]);count=best=0
    for _,d in events:count+=d;best=max(best,count)
    return scalar(best)
def minimum_interval_to_include_each_query(data):
    q=Numbers(data);a=sorted(q.rows(2));queries=q.vector();heap=[];i=0;out=[-1]*len(queries)
    for x,j in sorted((x,j) for j,x in enumerate(queries)):
        while i<len(a) and a[i][0]<=x:
            l,r=a[i];heapq.heappush(heap,(r-l+1,r));i+=1
        while heap and heap[0][1]<x:heapq.heappop(heap)
        if heap:out[j]=heap[0][0]
    return row(out)
def rotate_image(data):
    q=Numbers(data);n=q.one();a=[q.one() for _ in range(n*n)];return row(a[(n-1-j)*n+i] for i in range(n) for j in range(n))
def set_matrix_zeroes(data):
    r,c,a=grid(data);rs=set();cs=set()
    for u,x in enumerate(a):
        if x==0:i,j=divmod(u,c);rs.add(i);cs.add(j)
    return row(0 if i in rs or j in cs else a[i*c+j] for i in range(r) for j in range(c))
def happy_number(data):
    def step(x):
        total=0
        while x:x,d=divmod(x,10);total+=d*d
        return total
    out=[]
    for x in Numbers(data).vector():
        slow=fast=x
        while True:
            slow=step(slow);fast=step(step(fast))
            if slow==fast:break
        out.append(int(slow==1))
    return row(out)
def powx_n(data):
    tokens=data.split();out=[]
    for i in range(int(tokens[0])):
        a=float(tokens[1+2*i]);n=int(tokens[2+2*i]);negative=n<0;n=abs(n);result=1.0
        while n:
            if n%2:result*=a
            n//=2
            if n:a*=a
        if negative:result=1.0/result
        out.append(format(result,'.17e'))
    return ('\n'.join(out)+('\n' if out else '')).encode()
def multiply_strings(data):
    a,b=data.splitlines()[:2];out=[0]*(len(a)+len(b))
    for i in range(len(a)-1,-1,-1):
        for j in range(len(b)-1,-1,-1):
            x=out[i+j+1]+(a[i]-48)*(b[j]-48);out[i+j+1]=x%10;out[i+j]+=x//10
    result=''.join(map(str,out)).lstrip('0') or '0';return (result+'\n').encode()
def detect_squares(data):
    lines=data.splitlines();by_x={};counts=collections.Counter();out=[]
    for line in lines[1:1+int(lines[0])]:
        op,x,y=line.split();x,y=int(x),int(y)
        if op==b'+':counts[x,y]+=1;by_x.setdefault(x,set()).add(y)
        else:
            total=0
            for y2 in by_x.get(x,set()):
                if y2==y:continue
                d=y2-y
                for x2 in (x-d,x+d):total+=counts[x,y2]*counts[x2,y]*counts[x2,y2]
            out.append(total)
    return rows([x] for x in out)
def number_of_1_bits(data):return row(x.bit_count() for x in Numbers(data).vector())
def counting_bits(data):
    n=int(data);a=[0]*(n+1)
    for i in range(1,n+1):a[i]=a[i//2]+i%2
    return row(a)
def reverse_bits(data):return row(int(f'{x:032b}'[::-1],2) for x in Numbers(data).vector())
def missing_number(data):
    a=Numbers(data).vector();return scalar(len(a)*(len(a)+1)//2-sum(a))
def sum_of_two_integers(data):
    q=Numbers(data);out=[]
    for _ in range(q.one()):
        a,b=q.one()&0xffffffff,q.one()&0xffffffff
        while b:a,b=(a^b)&0xffffffff,((a&b)<<1)&0xffffffff
        out.append(a if a<0x80000000 else a-0x100000000)
    return row(out)

# Only task kernels enter the exported registry; helpers remain dependencies.
import json
from pathlib import Path
_TASK_IDS=[t['id'] for t in json.loads(Path(__file__).with_name('tasks.json').read_text())['tasks']]
SOLVERS={slug:globals()[slug.replace('-','_') if slug!='3sum' else 'three_sum'] for slug in _TASK_IDS}
