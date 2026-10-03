import sys,re,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
SUITE=HERE.parents[1]
sys.path.insert(0,str(HERE))
from attribution import NIL_LEX,pairs,split_top
from density import Vocabulary,MODELS
from external_suite import load_tasks
import tiktoken
BASELINE='920e510'
def read_source(task):
 return subprocess.check_output(['git','show',BASELINE+':corpora/application-v5/programs/'+task+'.nil'],cwd=SUITE,text=True)
def swap(text,mapping):
 out=[];cursor=0
 for m in NIL_LEX.finditer(text):
  out.append(text[cursor:m.start()]);v=m.group()
  # Function references share spelling with positional values; never rewrite calls.
  if v in mapping and not text[m.end():].lstrip().startswith('('):v=mapping[v]
  out.append(v);cursor=m.end()
 out.append(text[cursor:]);return ''.join(out)
def each_source(source):
 changes=[];closing=pairs(source)
 for m in NIL_LEX.finditer(source):
  if m.group()!='@':continue
  start=m.start();opening=m.end();end=closing[opening]
  parts=split_top(source,opening+1,end,';',closing)
  if len(parts)!=4:continue
  init=split_top(source,*parts[0],',',closing);steps=split_top(source,*parts[2],',',closing)
  if len(init)<3 or len(init)!=len(steps):continue
  chunks=lambda spans:[source[s:e] for s,e in spans]
  iv,sv=chunks(init),chunks(steps)
  condition=source[slice(*parts[1])];finish=source[slice(*parts[3])]
  if iv[1]!='0' or condition!='b<#a' or sv[:2]!=['a','b+1']:continue
  body=','.join(sv[2:])
  if '@' in body or '@' in finish:continue
  # Replace checked snapshot element expressions first, then rename index b->a.
  body=body.replace('a[b]','\ue000')
  tokens=list(NIL_LEX.finditer(body))
  if any(t.group()=='a' and not body[t.end():].lstrip().startswith('(') for t in tokens):continue
  if any(t.group() in ['a','b'] and not finish[t.end():].lstrip().startswith('(') for t in NIL_LEX.finditer(finish)):continue
  body=swap(body,{'b':'a'}).replace('\ue000','b')
  finish=swap(finish,{chr(97+i):chr(97+i-2) for i in range(2,len(iv))})
  candidate='!each('+iv[0]+','+','.join(iv[2:])+';'+body+';'+finish+')'
  changes.append((start,end+1,candidate))
 # Nonoverlapping selected regions only.
 for start,end,new in reversed(changes):source=source[:start]+new+source[end:]
 return source
SORT_GRADE='''(s,s)=!write(b,b(!read(a)))
(s):s=h(!sort(c(a),1))
(s):m=@(a,0,!map();b<#a;a,d(a,b),!has(c,e(a,b))?c:!insert(c,e(a,b),g(a,b));c)
(s,i)=!find(a,10,b)<#a?!find(a,10,b)+1:#a
(s,i):s=f(a,!find(a,9,b)+1,!find(a,10,b))
(s,i,i):s=!slice(a,b,c-b)
(s,i)=!parse(!slice(a,b,!find(a,9,b)-b))
(m):s=@(a,0,"";b<!size(a);a,b+1,!concat(c,!concat(!key(a,b),"\\n"));c)
'''
SORT_ETL=read_source('ex_etl').replace('(s):s=e(c(a))','(s):s=e(!sort(c(a),0))').splitlines()
SORT_ETL[-1]='(m):s=@(a,0,"";b<!size(a);a,b+1,!concat(c,!concat(b>0?",":"",!concat(!concat("\\\"",!concat(!key(a,b),"\\\":")),!format(!get(a,!key(a,b))))));!concat("{",!concat(c,"}")))'
SORT_ETL='\n'.join(SORT_ETL)+'\n'
JOINT_GRADE=SORT_GRADE.splitlines();JOINT_GRADE[-1]='(m):s=!each(a,"";!concat(c,!concat(a,"\\n"));a)';JOINT_GRADE='\n'.join(JOINT_GRADE)+'\n'
JOINT_ETL=SORT_ETL.splitlines();JOINT_ETL[-1]='(m):s=!each(a,"";!concat(c,!concat(#c>0?",":"",!concat(!concat("\\\"",!concat(a,"\\\":")),!format(b))));!concat("{",!concat(a,"}")))';JOINT_ETL='\n'.join(JOINT_ETL)+'\n'
vocabs=[Vocabulary(k,Path.home()/'.ollama/models') for k in MODELS]
encs={k:tiktoken.get_encoding(k) for k in ['cl100k_base','o200k_base']}
def counts(s):return {v.metadata['id']:len(v.ids(s)) for v in vocabs}|{k:len(e.encode(s,disallowed_special=())) for k,e in encs.items()}
rows=[]
try:
 for t in load_tasks('external'):
  if t['nil_status']=='unsupported':continue
  old=read_source(t['id']);before=counts(old)
  ordering=SORT_GRADE if t['id']=='ex_grade_school' else SORT_ETL if t['id']=='ex_etl' else old
  each=each_source(old)
  joint=JOINT_GRADE if t['id']=='ex_grade_school' else JOINT_ETL if t['id']=='ex_etl' else each_source(ordering)
  classification=old
  for index,line in enumerate(old.splitlines()):
   replacements={'1:b=a>=65?(a<=90?true:(a>=97?a<=122:false)):false':'1:b=!classify(a,0)',
     '1:b=a>=97?(a<=122?true:false):(a>=48?a<=57:false)':'1:b=!classify(a,2)'}
   if line in replacements:classification=classification.replace(line,replacements[line])
  compare=old
  if t['id']=='ex_grade_school':
   ls=old.splitlines();ls[10]=ls[10].replace('l(e(a,b),e(a,c))','!compare(e(a,b),e(a,c))<0');compare='\n'.join(ls[:11])+'\n'
  for candidate,source in [('sort',ordering),('each',each),('sort_each',joint),('classify',classification),('compare',compare)]:
   after=counts(source);rows.append({'task':t['id'],'candidate':candidate,'before':before,'after':after,'savings':{k:before[k]-after[k] for k in before},'prototype':source})
 totals={c:{k:sum(r['savings'][k] for r in rows if r['candidate']==c) for k in (*MODELS,*encs)} for c in ['sort','each','sort_each','classify','compare']}
 out={'warning':'UNVERIFIED lexical forecasts. No oracle/compiler/source modified. Same complete external population. Sort+each savings measured jointly, never added.','totals':totals,'records':rows}
 Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/nil-algorithms/forecast.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(totals,indent=2))
finally:
 for v in vocabs:v.close()
