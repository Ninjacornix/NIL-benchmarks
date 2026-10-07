"""Original deterministic inputs, frozen before NIL sample authoring."""
import random
from pathlib import Path

def vector(a): return str(len(a))+' '+ ' '.join(map(str,a))+'\n'
def matrix(a): return str(len(a))+'\n'+''.join(' '.join(map(str,x))+'\n' for x in a)
def chain(values,rng):
    ids=list(range(len(values))); rng.shuffle(ids); nodes=[[0,-1] for _ in ids]
    for i,node in enumerate(ids): nodes[node]=[values[i],ids[i+1] if i+1<len(ids) else -1]
    return f'{len(ids)} {ids[0] if ids else -1}\n'+''.join(f'{x} {y}\n' for x,y in nodes)
def indexed_tree(n,rng,mode):
    if not n: return '0 -1\n'
    ids=list(range(n)); rng.shuffle(ids); nodes=[[0,-1,-1] for _ in ids]
    # Inorder monotone values; left chain is a valid but deeply skewed BST.
    if mode=='chain':
        for i,node in enumerate(ids): nodes[node]=[n-i,ids[i+1] if i+1<n else -1,-1]
        root=ids[0]
    else:
        def build(lo,hi):
            if lo==hi: return -1
            m=(lo+hi)//2; node=ids[m]; nodes[node]=[m,build(lo,m),build(m+1,hi)]; return node
        root=build(0,n)
        if mode=='invalid' and n>1: nodes[ids[0]][0]=n+1
    return f'{n} {root}\n'+''.join(' '.join(map(str,x))+'\n' for x in nodes)
def fixture(slug,size,seed=419):
    r=random.Random(seed); n=size
    if slug=='contains-duplicate': return vector([r.randrange(-n,n+1) for _ in range(n)])
    if slug=='valid-sudoku':
        a=[0]*81
        if n: a=[(i//9*3+i//27+i%9)%9+1 for i in range(81)]
        if n==2: a[1]=a[0]
        return ' '.join(map(str,a))+'\n'
    if slug=='3sum': return vector([i-n//2 for i in range(n)])
    if slug=='valid-palindrome': return ('A man!'*(n//6)+'7')[:n]
    if slug=='longest-substring-without-repeating-characters': return ''.join(chr(r.randrange(32,127)) for _ in range(n))
    if slug=='longest-repeating-character-replacement': return str(n//7)+'\n'+''.join(chr(r.randrange(65,91)) for _ in range(n))
    if slug=='car-fleet':
        p=list(range(n)); r.shuffle(p); return f'{n+101}\n'+matrix([[x,r.randrange(1,101)] for x in p])
    if slug=='generate-parentheses': return str(n)+'\n'
    if slug=='median-of-two-sorted-arrays':
        a=sorted(r.randrange(-1000000,1000001) for _ in range(max(1,n)))
        return vector(a[::2])+vector(a[1::2])
    if slug=='search-in-rotated-sorted-array':
        a=list(range(n)); cut=r.randrange(n) if n else 0; a=a[cut:]+a[:cut]
        return vector(a)+str((seed%3)*(n//2) if n else 9)+'\n'
    if slug=='reverse-linked-list': return chain([r.randrange(-100,101) for _ in range(n)],r)
    if slug=='lru-cache':
        cap=max(0,n//3); ops=[]
        for i in range(n):
            key=r.randrange(max(1,n//2))
            ops.append(f'0 {key} {i}' if i%3 else f'1 {key}')
        return f'{cap} {n}\n'+'\n'.join(ops)+ ('\n' if ops else '')
    if slug in ('balanced-binary-tree','validate-binary-search-tree'): return indexed_tree(n,r,('chain','balanced','invalid')[seed%3])
    if slug=='implement-trie-prefix-tree':
        words=[''.join(chr(r.randrange(97,123)) for _ in range(8)) for _ in range(max(1,n//3))]
        ops=[('+','=','=')[i%3]+' '+words[(i//3)%len(words)] for i in range(n)]
        return str(n)+'\n'+'\n'.join(ops)+('\n' if ops else '')
    if slug=='word-search-ii':
        rows=cols=12 if n>100 else max(1,min(5,n)); words=set()
        count=min(30000,max(1,n//10))
        while len(words)<count: words.add(''.join(chr(r.randrange(97,123)) for _ in range(10)))
        board=[''.join(chr(r.randrange(97,123)) for _ in range(cols)) for _ in range(rows)]
        words.update(board); words.add(board[0][0]); words=sorted(words)
        # Bound dictionary aggregate <=300000 bytes including deliberately reachable words.
        while sum(map(len,words))>300000: words.pop()
        return f'{rows} {cols}\n'+'\n'.join(board)+f'\n{len(words)}\n'+'\n'.join(words)+'\n'
    if slug=='last-stone-weight': return vector([r.randrange(1,100001) for _ in range(n)])
    if slug=='kth-largest-element-in-an-array': return vector([r.randrange(-1000000,1000001) for _ in range(max(1,n))])+str(max(1,n//2))+'\n'
    if slug=='n-queens': return str(n)+'\n'
    if slug=='letter-combinations-of-a-phone-number': return ''.join('279'[r.randrange(3)] for _ in range(n))
    if slug in ('course-schedule','course-schedule-ii'):
        edges=[(i,i+1) for i in range(max(0,n-1))]
        edges += [(i,i+2) for i in range(max(0,n-2))]
        if seed%2 and n>1: edges.append((n-1,0))
        r.shuffle(edges); return f'{n} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)
    if slug=='network-delay-time':
        n=max(1,n); edges=[(i,i+1,r.randrange(1,101)) for i in range(n-1)]+[(i,i+2,1) for i in range(n-2)]
        r.shuffle(edges); return f'{n} {len(edges)} 0\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
    if slug=='cheapest-flights-within-k-stops':
        n=max(2,n); edges=[(i,i+1,1) for i in range(n-1)]+[(0,n-1,99)]
        return f'{n} {len(edges)} 0 {n-1} {min(n-1,100)}\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges)
    if slug=='min-cost-climbing-stairs': return vector([r.randrange(1001) for _ in range(max(2,n))])
    if slug=='coin-change': return vector([3,7,19,47])+str(n)+'\n'
    if slug=='target-sum': return vector([r.randrange(0,26) for _ in range(n)])+'0\n'
    if slug=='best-time-to-buy-and-sell-stock-with-cooldown': return vector([r.randrange(1001) for _ in range(n)])
    if slug=='gas-station':
        gas=[r.randrange(100) for _ in range(n)]; costs=[r.randrange(100) for _ in range(n)]
        return vector(gas)+vector(costs)
    if slug=='maximum-subarray': return vector([r.randrange(-1000,1001) for _ in range(max(1,n))])
    if slug in ('meeting-rooms','insert-interval'):
        intervals=[(3*i,3*i+2) for i in range(n)]
        if slug=='meeting-rooms':
            if seed%2 and n>1: intervals[-1]=(intervals[-2][0]+1,intervals[-1][1])
            r.shuffle(intervals)
        return matrix(intervals)+(f'{n} {2*n+1}\n' if slug=='insert-interval' else '')
    if slug=='plus-one': return vector([9]*max(1,n))
    if slug=='spiral-matrix':
        rows=max(0,int(math_sqrt(n))); cols=n//rows if rows else 0
        return f'{rows} {cols}\n'+' '.join(str(i) for i in range(rows*cols))+'\n'
    if slug=='single-number':
        a=list(range((n-1)//2))*2+[(-2147483648 if seed%2 else 2147483647)]; r.shuffle(a); return vector(a)
    if slug=='reverse-integer': return vector([r.randrange(-2147483648,2147483648) for _ in range(n)])
    raise NotImplementedError(slug)

def math_sqrt(n): return n**0.5

EDGES={
'contains-duplicate':['0\n','1 8\n','3 -4 2 -4\n'],
'valid-sudoku':[' '.join(['0']*81)+'\n'],
'3sum':['0\n','3 0 0 0\n','7 -8 3 5 -2 -1 3 0\n'],
'valid-palindrome':['','Aa!','12a21','aB'],
'longest-substring-without-repeating-characters':['','aaa','abca'],
'longest-repeating-character-replacement':['0\n','2\nABBAABA','0\nABCA'],
'car-fleet':['20\n0\n','20\n2\n4 4\n12 2\n'],
'generate-parentheses':['0\n','1\n','3\n'],
'median-of-two-sorted-arrays':['0\n1 -3\n','1 -5\n1 4\n','3 0 0 0\n2 0 0\n'],
'search-in-rotated-sorted-array':['0\n8\n','1 5\n5\n','4 5 8 -2 1\n8\n'],
'reverse-linked-list':['0 -1\n','3 2\n6 -1\n4 0\n9 1\n'],
'lru-cache':['0 3\n0 3 7\n1 3\n1 0\n','1 6\n0 5 8\n1 5\n0 6 9\n1 5\n0 6 10\n1 6\n'],
'balanced-binary-tree':['0 -1\n','3 0\n1 1 -1\n2 2 -1\n3 -1 -1\n'],
'validate-binary-search-tree':['0 -1\n','3 0\n5 1 2\n4 -1 -1\n5 -1 -1\n'],
'implement-trie-prefix-tree':['0\n','5\n+ \n= \n? \n+ bird\n? bi\n'],
'word-search-ii':['1 1\na\n3\na\nb\naa\n','2 2\nab\ncd\n4\nab\nac\nad\naba\n'],
'last-stone-weight':['0\n','2 8 8\n','3 15 4 9\n'],
'kth-largest-element-in-an-array':['1 -4\n1\n','4 3 3 -1 9\n2\n'],
'n-queens':['0\n','2\n','4\n'],
'letter-combinations-of-a-phone-number':['','2','97'],
'course-schedule':['0 0\n','2 2\n0 1\n1 0\n'],
'course-schedule-ii':['0 0\n','4 2\n0 3\n1 2\n','1 1\n0 0\n'],
'cheapest-flights-within-k-stops':['3 3 0 2 0\n0 1 2\n1 2 2\n0 2 7\n','2 0 0 1 5\n'],
'network-delay-time':['1 0 0\n','3 1 0\n0 1 2\n'],
'min-cost-climbing-stairs':['2 8 5\n','3 0 0 0\n'],
'coin-change':['0\n0\n','1 7\n8\n'],
 'target-sum':['0\n0\n','3 0 0 0\n0\n','2 3 4\n-7\n'],
'best-time-to-buy-and-sell-stock-with-cooldown':['0\n','5 2 4 7 0 3\n'],
'gas-station':['0\n0\n','3 3 1 1\n3 2 2 1\n'],
'maximum-subarray':['1 -8\n','4 -3 -8 -1 -5\n'],
'meeting-rooms':['0\n','2\n0 4\n4 9\n'],
'insert-interval':['0\n-3 4\n','2\n0 2\n5 7\n2 5\n'],
'plus-one':['1 0\n','4 8 9 9 9\n'],
'spiral-matrix':['0 3\n','1 4\n3 6 9 12\n','3 1\n4 5 6\n'],
'single-number':['1 -2147483648\n','5 -3 0 -3 8 8\n'],
'reverse-integer':['5 0 -100 1534236469 -2147483648 1463847412\n']}

def cases(task):
    slug=task['id']
    for i,data in enumerate(EDGES.get(slug,[])): yield f'edge-{i}',data.encode()
    cap=task['contract']['largest_size']
    for seed in (1907,2917,3919,4931):
        small=min(cap,6 if slug in ('generate-parentheses','n-queens','letter-combinations-of-a-phone-number') else 30)
        yield f'seed-{seed}',fixture(slug,small,seed).encode()
    yield 'largest',fixture(slug,cap,9918).encode()

_selected_fixture=fixture

def word_id(n,width=8):
    out=[]
    for _ in range(width):out.append(chr(97+n%26));n//=26
    return ''.join(out)
def fixture(slug,size,seed=419):
    if slug in EDGES:return _selected_fixture(slug,size,seed)
    rng=random.Random(seed);n=size
    values=[rng.randrange(-1000,1001) for _ in range(n)]
    nonnegative=[rng.randrange(0,1001) for _ in range(n)]
    letters=lambda length: ''.join(chr(rng.randrange(97,123)) for _ in range(length))
    if slug=='valid-anagram':
        a=letters(n);b=list(a);rng.shuffle(b)
        if seed%2 and b:b[0]='z' if b[0]!='z' else 'a'
        return a+'\n'+''.join(b)+'\n'
    if slug in ('two-sum','two-sum-ii-input-array-is-sorted'):
        a=list(range(2,max(2,n)+2));a[0]=0;a[-1]=1000000
        if slug=='two-sum':rng.shuffle(a)
        return vector(a)+'1000000\n'
    if slug=='group-anagrams':
        a=[word_id(i//2) for i in range(n)];a=[w[::-1] if i%2 else w for i,w in enumerate(a)]
        return str(n)+'\n'+'\n'.join(a)+ ('\n' if a else '')
    if slug=='top-k-frequent-elements':
        a=values or [7];return vector(a)+str(min(7,len(set(a))))+'\n'
    if slug=='product-of-array-except-self':return vector([(-1,0,1)[rng.randrange(3)] for _ in range(n)])
    if slug=='encode-and-decode-strings':
        a=[bytes([0,10,255,32])+word_id(i).encode() for i in range(n)]
        return (str(n).encode()+b'\n'+b''.join(str(len(x)).encode()+b'\n'+x for x in a))
    if slug=='longest-consecutive-sequence':return vector(values)
    if slug in ('container-with-most-water','trapping-rain-water','best-time-to-buy-and-sell-stock','daily-temperatures','largest-rectangle-in-histogram','house-robber','house-robber-ii'):return vector(nonnegative)
    if slug=='permutation-in-string':return letters(min(26,n))+'\n'+letters(n)+'\n'
    if slug=='minimum-window-substring':return letters(n)+'\n'+letters(min(30,n))+'\n'
    if slug=='sliding-window-maximum':return vector(values or [0])+str(max(1,n//11))+'\n'
    if slug=='valid-parentheses':return ('('*(n//2)+')'*(n//2)) if seed%2==0 else ('['*(n//2)+')'*(n//2))
    if slug=='min-stack':
        ops=[];depth=0
        for i in range(n):
            if depth==0 or i%4==0:ops.append('push '+str(i));depth+=1
            elif i%4==1:ops.append('min')
            elif i%4==2:ops.append('top')
            else:ops.append('pop');depth-=1
        return str(n)+'\n'+'\n'.join(ops)+'\n'
    if slug=='evaluate-reverse-polish-notation':
        # Long left-associated expression with signed arithmetic and bounded result.
        count=max(1,(n+1)//2);tokens=['-3']
        for i in range(count-1):tokens+=['2','+' if i%2 else '-']
        return str(len(tokens))+'\n'+' '.join(tokens)+'\n'
    if slug=='binary-search':return vector(list(range(n)))+str(n//2 if seed%2==0 else -3)+'\n'
    if slug=='search-a-2d-matrix':return f'1 {n}\n'+' '.join(str(i) for i in range(n))+f'\n{n//2}\n'
    if slug=='koko-eating-bananas':return vector([x+1 for x in nonnegative] or [1])+str(max(1,n)*3)+'\n'
    if slug=='find-minimum-in-rotated-sorted-array':
        a=list(range(max(1,n)));cut=len(a)//3;return vector(a[cut:]+a[:cut])
    if slug=='time-based-key-value-store':
        ops=[('set '+word_id(i%37)+f' {i} '+word_id(i)) if i%3 else ('get '+word_id(i%37)+f' {max(0,i-1)}') for i in range(n)]
        return str(n)+'\n'+'\n'.join(ops)+'\n'
    if slug in ('merge-two-sorted-lists','add-two-numbers'):
        a=sorted(values);b=sorted(values[::-1])
        if slug=='add-two-numbers':a=[rng.randrange(10) for _ in range(max(1,n))];b=[rng.randrange(10) for _ in range(max(1,n))];a[-1]=b[-1]=1
        return vector(a)+vector(b)
    if slug=='reorder-list':return vector(values)
    if slug in ('remove-nth-node-from-end-of-list','reverse-nodes-in-k-group'):return vector(values or [0])+str(max(1,n//7))+'\n'
    if slug in ('copy-list-with-random-pointer','linked-list-cycle'):
        base=chain(values,rng).splitlines();lines=[]
        for i,line in enumerate(base[1:]):
            val,nxt=map(int,line.split())
            if slug=='linked-list-cycle' and seed%2 and nxt==-1 and n:nxt=int(base[0].split()[1])
            lines.append(f'{val} {nxt}'+(f' {rng.randrange(-1,n)}' if slug=='copy-list-with-random-pointer' else ''))
        return base[0]+'\n'+'\n'.join(lines)+ ('\n' if lines else '')
    if slug=='find-the-duplicate-number':
        a=list(range(1,max(1,n)+1))+[max(1,n)//2 or 1];rng.shuffle(a);return vector(a)
    if slug=='merge-k-sorted-lists':
        k=min(31,max(1,n));parts=[sorted(values[i::k]) for i in range(k)]
        return str(k)+'\n'+''.join(vector(a) for a in parts)
    if slug in ('invert-binary-tree','maximum-depth-of-binary-tree','diameter-of-binary-tree','binary-tree-level-order-traversal','binary-tree-right-side-view','count-good-nodes-in-binary-tree','serialize-and-deserialize-binary-tree'):return indexed_tree(n,rng,'chain' if seed%2 else 'balanced')
    if slug=='binary-tree-maximum-path-sum':return indexed_tree(max(1,n),rng,'chain' if seed%2 else 'balanced')
    if slug in ('same-tree','subtree-of-another-tree'):
        a=indexed_tree(n,rng,'balanced');b=indexed_tree(n if slug=='same-tree' else n//3,rng,'balanced');return a+b
    if slug in ('lowest-common-ancestor-of-a-binary-search-tree','kth-smallest-element-in-a-bst'):
        a=indexed_tree(max(1,n),rng,'balanced');return a+(f'0 {max(0,n-1)}\n' if slug.startswith('lowest') else str(max(1,n//2))+'\n')
    if slug=='construct-binary-tree-from-preorder-and-inorder-traversal':
        # Ascending traversals intentionally produce a depth-n right chain.
        return vector(list(range(n)))+vector(list(range(n)))
    if slug=='design-add-and-search-words-data-structure':
        ops=[]
        for i in range(n):
            w=word_id(i//3)
            ops.append('+ '+w if i%3==0 else '? '+(w if i%3==1 else '.'+w[1:]))
        return str(n)+'\n'+'\n'.join(ops)+'\n'
    if slug=='kth-largest-element-in-a-stream':
        a=values or [0];return '1\n'+vector(a[:1])+vector(a)
    if slug=='k-closest-points-to-origin':return f'{n} {n//2}\n'+''.join(f'{i} {i%37}\n' for i in range(n))
    if slug=='task-scheduler':return '3\n'+''.join(chr(rng.randrange(65,91)) for _ in range(n))
    if slug=='design-twitter':
        ops=[(f'post {i%37} {i}' if i%4==0 else f'feed {i%37}' if i%4==1 else f'follow {i%37} {(i+1)%37}' if i%4==2 else f'unfollow {i%37} {(i+1)%37}') for i in range(n)]
        return str(n)+'\n'+'\n'.join(ops)+'\n'
    if slug=='find-median-from-data-stream':return vector(values)
    if slug in ('subsets','subsets-ii','permutations'):return vector(list(range(n)) if slug!='subsets-ii' else [i//2 for i in range(n)])
    if slug in ('combination-sum','combination-sum-ii'):
        return vector(list(range(1,n+1)) if slug=='combination-sum' else [(i%10)+1 for i in range(n)])+'20\n'
    if slug=='word-search':
        r=c=max(1,min(12,int(math_sqrt(n))));board=[letters(c) for _ in range(r)];word=board[0][:min(12,c)] if seed%2 else 'zzzzzzzzzzzz'
        return f'{r} {c}\n'+'\n'.join(board)+'\n'+word+'\n'
    if slug=='palindrome-partitioning':return ('a'*n if seed%2 else letters(n))+'\n'
    if slug in ('number-of-islands','max-area-of-island','pacific-atlantic-water-flow','surrounded-regions','rotting-oranges','walls-and-gates','longest-increasing-path-in-a-matrix','set-matrix-zeroes'):
        r=max(1,int(math_sqrt(n)));c=n//r;a=[]
        for i in range(r*c):
            x=rng.randrange(2)
            if slug in ('pacific-atlantic-water-flow','longest-increasing-path-in-a-matrix'):x=i if seed%2 else rng.randrange(1000)
            if slug=='rotting-oranges':x=2 if i%997==0 else x
            if slug=='walls-and-gates':x=0 if i%997==0 else -1 if i%7==0 else 2147483647
            a.append(x)
        return f'{r} {c}\n'+' '.join(map(str,a))+'\n'
    if slug in ('clone-graph','redundant-connection','number-of-connected-components-in-an-undirected-graph','graph-valid-tree'):
        n=max(3,n) if slug=='redundant-connection' else max(1,n);edges=[(i,i+1) for i in range(n-1)]
        if slug=='redundant-connection':edges.append((0,n-1))
        elif seed%2 and n>1:edges=edges[::2]
        return f'{n} {len(edges)}\n'+''.join(f'{u} {v}\n' for u,v in edges)+('0\n' if slug=='clone-graph' else '')
    if slug=='word-ladder':
        words=[word_id(i,4) for i in range(max(1,n))];return words[0]+'\n'+words[-1]+'\n'+str(len(words))+'\n'+'\n'.join(words)+'\n'
    if slug=='reconstruct-itinerary':
        airports=['AAA']+['A'+chr(65+i%26)+chr(65+(i//26)%26) for i in range(n)]
        return str(n)+'\n'+''.join(a+' '+b+'\n' for a,b in zip(airports,airports[1:]))
    if slug=='min-cost-to-connect-all-points':return matrix([(i,i%31) for i in range(n)])
    if slug=='swim-in-rising-water':
        side=max(1,int(math_sqrt(n)));a=list(range(side*side));rng.shuffle(a);return str(side)+'\n'+' '.join(map(str,a))+'\n'
    if slug=='alien-dictionary':return str(n)+'\n'+'\n'.join(sorted(word_id(i) for i in range(n)))+ ('\n' if n else '')
    if slug=='climbing-stairs':return str(n)+'\n'
    if slug in ('longest-palindromic-substring','palindromic-substrings'):return 'a'*n if seed%2 else letters(n)
    if slug=='decode-ways':return ('10'*(n//2)+('2' if n%2 else ''))
    if slug=='maximum-product-subarray':return vector([(-1,0,1)[rng.randrange(3)] for _ in range(max(1,n))])
    if slug=='word-break':return 'ab'*(n//2)+'\n3\na\nab\nbab\n'
    if slug=='longest-increasing-subsequence':return vector(values)
    if slug=='partition-equal-subset-sum':return vector([rng.randrange(1,1001) for _ in range(n)])
    if slug=='unique-paths':return f'2 {max(1,n//2)}\n'
    if slug in ('longest-common-subsequence','edit-distance'):return letters(n)+'\n'+letters(n)+'\n'
    if slug=='coin-change-ii':return vector([1,3,7])+str(n)+'\n'
    if slug=='interleaving-string':
        a=letters(n);b=letters(n);text=''.join(x+y for x,y in zip(a,b));return a+'\n'+b+'\n'+text+'\n'
    if slug=='distinct-subsequences':return 'a'*n+'\n'+'b'*n+'\n'
    if slug=='burst-balloons':return vector([rng.randrange(10) for _ in range(n)])
    if slug=='regular-expression-matching':return letters(n)+'\n'+'.*'*(n//2)+'\n'
    if slug in ('jump-game','jump-game-ii'):return vector([1 if i%3 else 3 for i in range(max(1,n))])
    if slug=='hand-of-straights':return vector([i//2 for i in range(n)])+'4\n'
    if slug=='merge-triplets-to-form-target-triplet':return matrix([[rng.randrange(11) for _ in range(3)] for _ in range(n)])+'10 10 10\n'
    if slug=='partition-labels':return letters(n)
    if slug=='valid-parenthesis-string':return '('* (n//3)+'*'*(n//3)+')'*(n//3)
    if slug in ('merge-intervals','non-overlapping-intervals','meeting-rooms-ii','minimum-interval-to-include-each-query'):
        a=[(i,i+1+rng.randrange(7)) for i in range(n)];rng.shuffle(a)
        return matrix(a)+(vector(list(range(n))) if slug.startswith('minimum') else '')
    if slug=='rotate-image':
        side=int(math_sqrt(n));return str(side)+'\n'+' '.join(str(i) for i in range(side*side))+'\n'
    if slug=='happy-number':return vector([rng.randrange(1,2147483648) for _ in range(n)])
    if slug=='powx-n':return str(n)+'\n'+''.join(f'1.0001 {rng.randrange(-1000,1001)}\n' for _ in range(n))
    if slug=='multiply-strings':return ('9'*max(1,n))+'\n'+('8'*max(1,n))+'\n'
    if slug=='detect-squares':
        ops=[(f'+ {i%101} {i//101}' if i%4 else f'? {i%101} {i//101}') for i in range(n)]
        return str(n)+'\n'+'\n'.join(ops)+'\n'
    if slug in ('number-of-1-bits','reverse-bits'):return vector([rng.randrange(2**32) for _ in range(n)])
    if slug=='counting-bits':return str(n)+'\n'
    if slug=='missing-number':
        a=list(range(n+1));del a[n//2];rng.shuffle(a);return vector(a)
    if slug=='sum-of-two-integers':return str(n)+'\n'+''.join(f'{rng.randrange(-2**31,2**31)} {rng.randrange(-2**31,2**31)}\n' for _ in range(n))
    raise NotImplementedError(slug)

_selected_cases=cases
def cases(task):
    if task['id'] in EDGES:yield from _selected_cases(task);return
    cap=task['contract']['largest_size']
    for name,size,seed in [('minimum',0,419),('singleton',1,420),('seed-1907',min(15,cap),1907),('seed-2917',min(15,cap),2917),('seed-3919',min(15,cap),3919),('seed-4931',min(15,cap),4931),('largest',cap,9919)]:
        # Named minimum means smallest legal input, not necessarily empty.
        data=fixture(task['id'],size,seed)
        yield name,data.encode() if isinstance(data,str) else data
