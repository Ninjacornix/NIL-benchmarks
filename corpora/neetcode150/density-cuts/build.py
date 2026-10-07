"""Separately authored typed kernels/adapters; frozen programs are never edited."""
import ast
import copy
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
CORPUS=HERE.parent
sys.path.insert(0,str(CORPUS))
import reference, cpp
VECTOR=['contains-duplicate','3sum','last-stone-weight','maximum-subarray','min-cost-climbing-stairs','plus-one','reverse-integer','best-time-to-buy-and-sell-stock-with-cooldown','single-number']
# Explicit decoded-input expressions, before inspecting token results. Parameters
# reflect actual typed data rather than a byte parser hidden inside a kernel.
D={t:[('a','Numbers(data).vector()')] for t in VECTOR}
D.update({
'car-fleet':[('target','q.one()'),('a','q.rows(2)')],
'coin-change':[('coins','q.vector()'),('amount','q.one()')],
'gas-station':[('gas','q.vector()'),('costs','q.vector()')],
'generate-parentheses':[('n','int(data)')],
'insert-interval':[('a','q.rows(2)'),('lo','q.one()'),('hi','q.one()')],
'kth-largest-element-in-an-array':[('a','q.vector()'),('k','q.one()')],
'median-of-two-sorted-arrays':[('a','q.vector()'),('b','q.vector()')],
'meeting-rooms':[('a','Numbers(data).rows(2)')],
'reverse-linked-list':[('n','q.one()'),('head','q.one()'),('a','[[q.one(), q.one()] for _ in range(n)]')],
'search-in-rotated-sorted-array':[('a','q.vector()'),('target','q.one()')],
'spiral-matrix':[('r','q.one()'),('c','q.one()'),('a','[[q.one() for _ in range(c)] for _ in range(r)]')],
'target-sum':[('a','q.vector()'),('target','q.one()')],
'valid-sudoku':[('a','list(map(int, data.split()))')],
'balanced-binary-tree':[('a','TREE_A'),('root','TREE_ROOT')],
'validate-binary-search-tree':[('a','TREE_A'),('root','TREE_ROOT')],
'course-schedule':[('n','GRAPH_N'),('edges','GRAPH_EDGES')],
'longest-repeating-character-replacement':[('k','LINE_K'),('line','LINE_TEXT')],
'letter-combinations-of-a-phone-number':[('data','data')],
'longest-substring-without-repeating-characters':[('data','data')],
'valid-palindrome':[('data','data')],
})
SER={t:'scalar' for t in D}
for t in ['plus-one','reverse-integer','reverse-linked-list','spiral-matrix']:SER[t]='row'
for t in ['3sum','insert-interval']:SER[t]='rows'
for t in ['generate-parentheses','letter-combinations-of-a-phone-number']:SER[t]='lines'

def expr(s):return ast.parse(s,mode='eval').body
def key(n):return ast.dump(n,include_attributes=False)
class Decode(ast.NodeTransformer):
 def visit_Call(self,n):
  if isinstance(n.func,ast.Attribute) and n.func.attr in ['one','vector','rows']:
   owner=n.func.value
   if isinstance(owner,ast.Call) and isinstance(owner.func,ast.Name) and owner.func.id=='Numbers':
    if n.func.attr=='vector':return expr('list(map(int,data.split()))[1:]')
    owner=ast.Name('q',ast.Load())
   if n.func.attr=='one':return ast.Call(ast.Name('next',ast.Load()),[owner],[])
   width=n.args[0] if n.args else None
   text='[next(q) for _ in range(next(q))]' if width is None else '[[next(q) for _ in range(WIDTH)] for _ in range(next(q))]'
   result=expr(text)
   class Names(ast.NodeTransformer):
    def visit_Name(self,x):
     if x.id=='q':return copy.deepcopy(owner)
     if x.id=='WIDTH':return copy.deepcopy(width)
     return x
   return Names().visit(result)
  return self.generic_visit(n)

class Kernel(ast.NodeTransformer):
 def __init__(self,task):
  self.task=task;self.replacements={}
  for name,s in D[task]:
   if not s.startswith(('TREE_','GRAPH_','LINE_')):self.replacements.setdefault(key(expr(s)),[]).append(name)
 def visit(self,n):
  if isinstance(n,ast.expr) and self.replacements.get(key(n)):return ast.Name(self.replacements[key(n)].pop(0),ast.Load())
  return super().visit(n)
 def visit_Assign(self,n):
  text=ast.unparse(n.value)
  if text=='Numbers(data)' or text in ['tree(data)','graph(data)',"data.split(b'\\n', 1)"] or self.task=='longest-repeating-character-replacement' and text=='int(k)':return None
  n=self.generic_visit(n)
  if len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Name) and n.targets[0].id==n.value.id:return None
  return n
 def visit_Return(self,n):
  if isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id in ['scalar','row','rows']:return ast.Return(self.visit(n.value.args[0]))
  return self.generic_visit(n)

def python(task):
 tree=ast.parse((CORPUS/'programs'/f'{task}.py').read_text());name=reference.SOLVERS[task].__name__
 fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
 fn=Kernel(task).visit(copy.deepcopy(fn));fn.name='kernel';fn.args.args=[ast.arg(n) for n,_ in D[task]]
 if task=='generate-parentheses':fn.body[-1]=ast.Return(ast.Name('out',ast.Load()))
 if task=='letter-combinations-of-a-phone-number':fn.body[-1]=ast.parse('return [bytes(x) for x in itertools.product(*(letters[d-50] for d in data))] if data else []').body[0]
 helpers=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='topological']
 used={n.id for x in [fn,*helpers] for n in ast.walk(x) if isinstance(n,ast.Name)}
 imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)) and any((a.asname or a.name.split('.')[0]) in used for a in n.names)]
 kernel='\n\n'.join(ast.unparse(ast.fix_missing_locations(n)) for n in [*imports,*helpers,fn])+'\n'
 dec=[]
 if task in ['balanced-binary-tree','validate-binary-search-tree']:
  dec=['q=iter(map(int,data.split()))','n=next(q)','root=next(q)','a=[[next(q),next(q),next(q)] for _ in range(n)]']
 elif task=='course-schedule':dec=['q=iter(map(int,data.split()))','n=next(q)','m=next(q)','edges=[[next(q),next(q)] for _ in range(m)]']
 elif task=='longest-repeating-character-replacement':dec=["k,line=data.split(b'\\n',1)",'k=int(k)']
 else:
  if any('q.' in s or '.rows(' in s for _,s in D[task]):dec=['q=iter(map(int,data.split()))']
  dec += [n+'='+ast.unparse(ast.fix_missing_locations(Decode().visit(expr(s)))) for n,s in D[task] if s!='data']
 call='kernel('+','.join(n for n,_ in D[task])+')';kind=SER[task]
 enc={'scalar':"(str(int(result))+'\\n').encode()",'row':"(' '.join(map(str,result))+'\\n').encode()",'rows':"b''.join((' '.join(map(str,r))+'\\n').encode() for r in result)",'lines':"b''.join((r.encode() if isinstance(r,str) else r)+b'\\n' for r in result)"}[kind]
 adapter='def solve(data):\n'+''.join('    '+s+'\n' for s in [*dec,'result='+call,'return '+enc])
 driver="\nif __name__ == '__main__':\n    import sys\n    from pathlib import Path\n    result=solve(Path(sys.argv[1]).read_bytes())\n    Path(sys.argv[2]).write_bytes(result)\n    print(len(result))\n"
 return kernel,kernel+'\n'+adapter+driver

# C++ adapters decode before invoking a typed kernel. The algorithm body comes
# from the original reference; only decoding and encoding boundaries change.
C={t:('V a','auto a=q.vector();','a') for t in VECTOR}
C.update({
'car-fleet':('I target,std::vector<V> a','I target=q.one();auto a=q.matrix(2);','target,a'),
'coin-change':('V coins,I amount','auto coins=q.vector();I amount=q.one();','coins,amount'),
'gas-station':('V gas,V cost','auto gas=q.vector(),cost=q.vector();','gas,cost'),
'generate-parentheses':('I n','I n=q.one();','n'),
'insert-interval':('std::vector<V> a,I lo,I hi','auto a=q.matrix(2);I lo=q.one(),hi=q.one();','a,lo,hi'),
'kth-largest-element-in-an-array':('V a,I k','auto a=q.vector();I k=q.one();','a,k'),
'median-of-two-sorted-arrays':('V a,V b','auto a=q.vector(),b=q.vector();','a,b'),
'meeting-rooms':('std::vector<V> a','auto a=q.matrix(2);','a'),
'reverse-linked-list':('std::vector<std::array<I,2>> a,I head','I n=q.one(),head=q.one();std::vector<std::array<I,2>> a(n);for(auto &r:a){r[0]=q.one();r[1]=q.one();}','a,head'),
'search-in-rotated-sorted-array':('V a,I target','auto a=q.vector();I target=q.one();','a,target'),
'spiral-matrix':('I r,I c,V a','I r=q.one(),c=q.one();V a(r*c);for(auto&x:a)x=q.one();','r,c,a'),
 'target-sum':('V a,I target','auto a=q.vector();I target=q.one();','a,target'),
'valid-sudoku':('V a','auto a=q.vector();','a'),
'balanced-binary-tree':('std::vector<std::array<I,3>> a,I root',cpp.TREE,'a,root'),
'validate-binary-search-tree':('std::vector<std::array<I,3>> a,I root',cpp.TREE,'a,root'),
'course-schedule':('I n,std::vector<V> edges','I n=q.one(),m=q.one();std::vector<V> edges(m,V(2));for(auto&r:edges)for(auto&x:r)x=q.one();','n,edges'),
'longest-repeating-character-replacement':('I k,std::string data',"I k=q.one();auto start=q.data.find('\\n')+1;auto data=q.data.substr(start);",'k,data'),
'letter-combinations-of-a-phone-number':('std::string data','','q.data'),
'longest-substring-without-repeating-characters':('std::string data','','q.data'),
'valid-palindrome':('std::string data','','q.data'),
})
def unwrap_calls(s):
 for name in ['scalar','rows','row']:
  marker='return '+name+'('
  while marker in s:
   start=s.index(marker);i=start+len(marker);depth=1;j=i
   while depth:
    if s[j]=='(':depth+=1
    if s[j]==')':depth-=1
    j+=1
   s=s[:start]+'return '+s[i:j-1]+s[j:]
 return s

def cxx(task):
 body=cpp.B[task];params,adapter,args=C[task]
 if task=='single-number':body=body.replace('q.vector()','a')
 elif task=='valid-sudoku':body=body.replace('q.one()','a[i]');adapter='V a(81);for(auto&x:a)x=q.one();'
 elif task=='course-schedule':
  body=body.replace('I n=q.one(),m=q.one();','').replace('for(I i=0;i<m;++i){I u=q.one(),v=q.one();','for(auto edge:edges){I u=edge[0],v=edge[1];')
 elif task=='longest-repeating-character-replacement':body=body.replace("I k=q.one();auto start=q.data.find('\\n')+1;",'').replace('q.data.size()-start','data.size()').replace('q.data[start+i]','data[i]').replace('q.data[start+left++]','data[left++]')
 elif task=='search-in-rotated-sorted-array':body=body.replace('auto a=q.vector();I target=q.one(),lo=0,hi=(I)a.size()-1;','I lo=0,hi=(I)a.size()-1;')
 elif task=='target-sum':body=body.replace('auto a=q.vector();I target=q.one(),total=0;','I total=0;')
 else:
  if adapter:assert body.startswith(adapter),(task,adapter);body=body[len(adapter):]
 body=body.replace('q.data','data');body=unwrap_calls(body)
 if task in ['balanced-binary-tree','validate-binary-search-tree']:body='I n=a.size();'+body
 if task=='generate-parentheses':body=body.replace('std::string out;','std::vector<std::string> out;').replace("out+=s+'\\n';",'out.push_back(s);')
 if task=='letter-combinations-of-a-phone-number':body=body.replace('return "";','return {};').replace('std::string out;','std::vector<std::string> out;').replace("out+=prefix+'\\n';",'out.push_back(prefix);')
 kind=SER[task];ret={'scalar':'I','row':'V','rows':'std::vector<V>','lines':'std::vector<std::string>'}[kind]
 original=(CORPUS/'programs'/f'{task}.cpp').read_text()
 headers='\n'.join(l for l in original.splitlines() if l.startswith('#include') and not any(x in l for x in ['charconv','fstream','iostream']) and not ('stdexcept' in l and 'runtime_error' not in body) and not ('string>' in l and 'string' not in body+params+ret))
 kernel=headers+'\nusing I=std::int64_t;\nusing V=std::vector<I>;\n'+ret+' kernel('+params+'){'+body+'}\n'
 io='''#include <fstream>
#include <iostream>
#include <sstream>
struct Input {std::string data;std::istringstream input;I one(){I x;input>>x;return x;}V vector(){V a(one());for(auto&x:a)x=one();return a;}std::vector<V> matrix(int w){std::vector<V>a(one(),V(w));for(auto&r:a)for(auto&x:r)x=one();return a;}};
std::string row(const V&a){std::string s;for(I x:a){if(!s.empty())s+=' ';s+=std::to_string(x);}return s+'\\n';}
'''
 enc={'scalar':"std::to_string(result)+'\\n'",'row':'row(result)','rows':'[&]{std::string s;for(auto&r:result)s+=row(r);return s;}()','lines':"[&]{std::string s;for(auto&r:result)s+=r+'\\n';return s;}()"}[kind]
 driver='int main(int argc,char**argv){if(argc!=3)return 2;std::ifstream file(argv[1],std::ios::binary);auto raw_input=std::string(std::istreambuf_iterator<char>(file),{});Input q{raw_input,std::istringstream(raw_input)};'+adapter+'auto result=kernel('+args+');auto answer='+enc+';std::ofstream out(argv[2],std::ios::binary);out<<answer;std::cout<<answer.size()<<\'\\n\';}\n'
 return kernel,kernel+io+driver

def main():
 manifest=[]
 for task in sorted(D):
  for lang,ext,build in [('python','py',python),('cpp','cpp',cxx)]:
   kernel,full=build(task)
   for cut,text in [('kernels',kernel),('minimal-io',full),('kernel-host',full)]:
    p=HERE/cut;p.mkdir(exist_ok=True);(p/(task+'.'+ext)).write_text(text)
   manifest.append({'task':task,'language':lang,'decoded_parameters':[n for n,_ in D[task]],'serialization':SER[task]})
 (HERE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('generated',len(D),'typed kernels and adapters per baseline; no frozen source edited')
if __name__=='__main__':main()

# NIL kernels keep the language's real flat-buffer input representation. Its
# offsets/count headers are charged, rather than pretending records-of-input
# have free construction. Only byte decoding/encoding adapters are excluded.
def nil(task):
 import re
 source=(CORPUS/'programs'/f'{task}.nil').read_text()
 records=[l for l in source.splitlines() if l.startswith('record ')]
 f=[l for l in source.splitlines() if not l.startswith('record ')]
 exclude={0,1}
 row_formatter='(v):s=@(a,"",0;c<#a;a,!concat(b,!concat(c==0?"":" ",!format(a[c]))),c+1;!concat(b,"\\n"))'
 if task in ['plus-one','reverse-integer','reverse-linked-list']:
  f[1]='(s):s=d(c(!parsebuf(a," \\n")))';f[2]=f[2].replace('(v):s=d(', '(v):v=')
  assert f[2].endswith(')');f[2]=f[2][:-1];exclude.add(3)
 if task=='spiral-matrix':exclude.add(3)
 if task=='3sum':
  # Materializing 1,124,250 triples exceeds 64 MiB once immutable aliases and
  # growth coexist. Stream typed triples through an explicit static callback;
  # formatting lives in the adapter, not in the counted algorithm.
  f[1]='(s):s=c(!parsebuf(a," \\n"),&h)'
  f[2]='(v,[s,i,i,i:s]):s=d(!sort(!slice(a,1,a[0]),0),^b)'
  f[3]=f[3].replace('(v):s=', '(v,[s,i,i,i:s]):s=').replace('e(a,b,c)', 'e(a,b,c,^b)')
  f[4]=f[4].replace('(v,i,s):s=', '(v,i,s,[s,i,i,i:s]):s=')
  old='!concat(e,!concat(!format(a[b]),!concat(" ",!concat(!format(a[c]),!concat(" ",!concat(!format(a[d]),"\\n"))))))'
  assert old in f[4];f[4]=f[4].replace(old,'^d(e,a[b],a[c],a[d])')
  exclude.add(len(f));f.append('(s,i,i,i):s=!concat(a,!concat(!format(b),!concat(" ",!concat(!format(c),!concat(" ",!concat(!format(d),"\\n"))))))')
 if task=='insert-interval':
  f[1]='(s):s=e(c(!parsebuf(a," \\n")))';f[2]=f[2].replace('(v):s=', '(v):v=').replace(',"",false;', ',!buffer(0,0),false;');f[3]='2:v=!buffer(2,0)[0:a][1:b]';f[2]=f[2].replace('f?"":d(c,d)', 'f?!buffer(0,0):d(c,d)')
  exclude.add(len(f));f.append('(v):s=@(a,"",0;c<#a;a,!concat(b,!concat(!format(a[c]),!concat(" ",!concat(!format(a[c+1]),"\\n")))),c+2;b)')
 if task=='generate-parentheses':
  f[1]='(s):s=c(!parsebuf(a," \\n"),&g)'
  f[2]='(v,[s:s]):s=d(a[0],0,0,"",^b)'
  f[3]='(i,i,i,s,[s:s]):s=c==a?^e(d):!concat(b<a?e(a,b,c,d,^e):"",c<b?f(a,b,c,d,^e):"")'
  f[4]='(i,i,i,s,[s:s]):s=d(a,b+1,c,!concat(d,"("),^e)'
  f[5]='(i,i,i,s,[s:s]):s=d(a,b,c+1,!concat(d,")"),^e)'
  exclude.add(len(f));f.append('(s):s=!concat(a,"\\n")')
 if task=='letter-combinations-of-a-phone-number':
  f[1]='(s):s=c(a,&f)'
  f[2]=f[2].replace('(s):s=', '(s,[s:s]):s=').replace('!concat(d,!concat(d(a,b),"\\n"))','!concat(d,^b(d(a,b)))')
  exclude.add(len(f));f.append('(s):s=!concat(a,"\\n")')
 # Kernel extraction renumbers positional functions; no parameter names change.
 included=[i for i in range(len(f)) if i not in exclude]
 names={chr(97+old):chr(97+new) for new,old in enumerate(included)}
 def rename(s):
  s=re.sub(r'(?<![!^a-z_])([a-z]+)\(',lambda m:names.get(m[1],m[1])+'(',s)
  return re.sub(r'&([a-z]+)',lambda m:'&'+names.get(m[1],m[1]),s)
 kernel='\n'.join([*records,*[rename(f[i]) for i in included]])+'\n'
 full='\n'.join([*records,*f])+'\n'
 return kernel,full

# Deliberately after the first main block: baselines are exported independently.
if __name__=='__main__':
 m=json.loads((HERE/'MANIFEST.json').read_text())
 for task in sorted(D):
  kernel,full=nil(task)
  for cut,text in [('kernels',kernel),('kernel-host',full),('minimal-io',(CORPUS/'programs'/(task+'.nil')).read_text())]:
   (HERE/cut/(task+'.nil')).write_text(text)
  m.append({'task':task,'language':'nil','decoded_parameters':'Current typed flat buffer/byte/record signatures; metadata offsets remain charged.','serialization':SER[task]})
 (HERE/'MANIFEST.json').write_text(json.dumps(m,indent=2)+'\n')
 print('generated 29 NIL typed kernels/adapters')
