import sys,re,json
from pathlib import Path
sys.path.insert(0,'benchmarks/corpora/application-v5')
from density import Vocabulary
import tiktoken
root=Path('benchmarks/corpora/application-v5/programs')
v=[Vocabulary(k,Path.home()/'.ollama/models') for k in ('gemma3_4b','qwen2.5_7b_instruct')]
e={k:tiktoken.get_encoding(k) for k in ('cl100k_base','o200k_base')}
def counts(s):
 return {**{x.metadata['id']:len(x.ids(s)) for x in v},**{k:len(x.encode(s,disallowed_special=())) for k,x in e.items()}}
rows=[]
for p in sorted(root.glob('*.nil')):
 s=p.read_text(); pattern=r'(?<![\w!.])([a-z]+)\('
 def replace(m):
  label=0
  for c in m[1]: label=label*26+ord(c)-96
  label-=1
  return '!plugin(1,'+str(label)+('' if s[m.end():].startswith(')') else ',')
 transformed=re.sub(pattern,replace,s)
 rows.append({'task':p.stem,'calls':len(re.findall(pattern,s)),'local':counts(s),'qualified':counts(transformed)})
result={'metric':'hypothetical qualification of every local call using existing !plugin(1,export,args) spelling; not a verified source rewrite','tokenizers':[x.metadata for x in v],'rows':rows,'cuts':{}}
for cut,rs in [('original',[r for r in rows if not r['task'].startswith('ex_')]),('external',[r for r in rows if r['task'].startswith('ex_')]),('combined',rows)]:
 result['cuts'][cut]={'programs':len(rs),'calls':sum(r['calls'] for r in rs),'tokens':{k:{'local':sum(r['local'][k] for r in rs),'qualified':sum(r['qualified'][k] for r in rs),'delta':sum(r['qualified'][k]-r['local'][k] for r in rs)} for k in rows[0]['local']}}
Path('/tmp/nil-modules/naming.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result['cuts'],indent=2))
for x in v:x.close()
