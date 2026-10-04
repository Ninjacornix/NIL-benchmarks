"""Independent executable contracts for externally derived algorithm intent."""
import json
from collections import deque

def expected(task,data):
 values=[int(s) for s in data.decode('ascii').replace('\n',',').split(',') if s]
 if task=='ex_algo_linked_list':
  nodes=list(zip(values[::2],values[1::2]));result=[];i=0 if nodes else -1;seen=set()
  while i!=-1:
   assert i not in seen and 0<=i<len(nodes);seen.add(i)
   value,i=nodes[i];result.append(value)
 elif task=='ex_algo_bst_walk':
  # In-order BST traversal must equal the sorted insertion multiset, independent
  # of the reference solution's tree representation/recursion.
  result=sorted(values)
 elif task=='ex_algo_graph_bfs':
  rows=[];i=0
  while i<len(values):
   n=values[i];rows.append(values[i+1:i+1+n]);assert n>=0 and len(rows[-1])==n;i+=n+1
  result=[];pending=deque([0] if rows else []);seen=set(pending)
  while pending:
   vertex=pending.popleft();result.append(vertex)
   for neighbor in rows[vertex]:
    assert 0<=neighbor<len(rows)
    if neighbor not in seen:seen.add(neighbor);pending.append(neighbor)
 elif task=='ex_algo_interval_merge':
  intervals=list(zip(values[::2],values[1::2]));result=[]
  # Endpoint sweep independently establishes connected closed unions.
  events=[]
  for lo,hi in intervals:assert lo<=hi;events.extend([(lo,0),(hi,1)])
  depth=0
  for x,closing in sorted(events):
   if not closing:
    if depth==0:start=x
    depth+=1
   else:
    depth-=1
    if depth==0:result.append([start,x])
 else:raise KeyError(task)
 return json.dumps(result,separators=(',',':')).encode()
