"""Exact kernel-token ledger. Categories partition tokens, not estimated removable work."""
import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
from pathlib import Path
import re
import io
import tokenize
import sys
import tiktoken
HERE=Path(__file__).resolve().parent
SUITE=HERE.parent
sys.path.insert(0,str(SUITE/'corpora/application-v5'))
from attribution import lexical_nil, pairs, split_top, paint, python_labels, ledger, CATEGORIES, NIL_LEX
KERNELS=SUITE/'corpora/neetcode150/density-cuts/kernels'
DENSITY=SUITE/'reports/2026-10-07/ROUND20_DENSITY.json'

def nil_labels(source):
 labels=lexical_nil(source);closing=pairs(source)
 # Header = through the declaration's first '='. Static function types contain
 # colons and nested brackets, but never '='. Body bindings are not headers.
 for line in re.finditer(r'[^\n]+',source):
  text=line.group()
  if text.startswith('record '):paint(labels,line.start(),line.end(),'record_definition')
  else:
   if not (text.startswith('(') or text[0].isdigit()):raise ValueError('unhandled declaration '+text)
   header=text.index('=')+1;paint(labels,line.start(),line.start()+header,'signature')
 for match in NIL_LEX.finditer(source):
  if match.group()!='@':continue
  opening=match.end();assert source[opening]=='(';end=closing[opening]
  sections=split_top(source,opening+1,end,';',closing)
  # Lexical bindings add top-level semicolons in the body: first two sections
  # are initial/condition; last is finish; intervening sections form the body.
  if len(sections)<4:raise ValueError('unhandled loop')
  for point in [match.start(),opening,end,sections[0][1],sections[1][1],sections[-2][1]]:
   paint(labels,point,point+1,'loop_delimiters')
  condition=source[slice(*sections[1])]
  if re.fullmatch(r'[a-z](?:<|<=|>|>=)(?:#[a-z]|[a-z]|\d+)',condition):
   paint(labels,*sections[1],'loop_index_bound')
  steps=split_top(source,*sections[-2],',',closing)
  for index,(start,stop) in enumerate(steps):
   name=chr(ord('a')+index);step=source[start:stop].strip()
   if step==name:paint(labels,start,stop,'unchanged_state')
   elif step in (name+'+1',name+'-1') and re.search(r'\b'+name+r'\b',condition):paint(labels,start,stop,'loop_index_bound')
 # A replacement colon is not a ternary colon. Track pending questions at
 # each delimiter depth; quoted punctuation is excluded by lexical iteration.
 stack=[['root',0]]
 for token in NIL_LEX.finditer(source):
  text=token.group()
  if text in ('(', '['):stack.append([text,0])
  elif text in (')', ']'):
   assert stack[-1][1]==0,'unmatched ternary';stack.pop()
  elif text=='?' and labels[token.start()]=='operator':
   stack[-1][1]+=1;paint(labels,token.start(),token.end(),'conditional')
  elif text==':' and labels[token.start()]=='operator':
   if stack[-1][1]:
    stack[-1][1]-=1;paint(labels,token.start(),token.end(),'conditional')
   elif stack[-1][0]=='[':paint(labels,token.start(),token.end(),'functional_update')
 assert len(stack)==1 and stack[0][1]==0
 return labels

def py_labels(source):
 labels=python_labels(source)[0];offsets=[0]
 for line in source.splitlines(keepends=True):offsets.append(offsets[-1]+len(line))
 for item in tokenize.generate_tokens(io.StringIO(source).readline):
  if item.type==tokenize.NAME and item.string in ('if','elif','else'):
   start=offsets[item.start[0]-1]+item.start[1];stop=offsets[item.end[0]-1]+item.end[1]
   paint(labels,start,stop,'conditional')
 return labels

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 frozen=json.loads(DENSITY.read_text());expected={(r['task'],r['language']):r for r in frozen['per_task'] if r['cut']=='kernel-only' and r['language'] in ('nil','python')}
 totals={n:{l:Counter() for l in ('nil','python')} for n in ('cl100k_base','o200k_base')};records=[]
 categories=(*CATEGORIES,'conditional','functional_update'); original_categories=ledger.__globals__['CATEGORIES'];ledger.__globals__['CATEGORIES']=categories
 for (task,language),row in sorted(expected.items()):
  path=KERNELS/(task+('.nil' if language=='nil' else '.py'));data=path.read_bytes();source=data.decode()
  assert hashlib.sha256(data).hexdigest()==row['sha256']
  labels=nil_labels(source) if language=='nil' else py_labels(source)
  for name in totals:
   enc=tiktoken.get_encoding(name);ids=enc.encode(source,disallowed_special=())
   assert len(ids)==row['tokens'][name]
   counts,fractions,spans=ledger(source,labels,[enc.decode_single_token_bytes(i) for i in ids])
   totals[name][language].update(counts)
   records.append(dict(task=task,language=language,tokenizer=name,sha256=row['sha256'],counts=counts,fractions=fractions,ledger=spans))
 ledger.__globals__['CATEGORIES']=original_categories
 ranked={};checks={}
 for name,langs in totals.items():
  ranked[name]=sorted([dict(category=c,nil=langs['nil'][c],python=langs['python'][c],difference=langs['nil'][c]-langs['python'][c]) for c in categories],key=lambda r:-r['difference'])
  nt=sum(langs['nil'].values());pt=sum(langs['python'].values());gap=sum(r['difference'] for r in ranked[name])
  assert nt==frozen['totals']['kernel-only']['nil']['tokens'][name] and pt==frozen['totals']['kernel-only']['python']['tokens'][name] and gap==nt-pt
  checks[name]=dict(nil=nt,python=pt,gap=gap,exact_sum=True)
 result=dict(schema=1,cohort=29,method=__doc__+' Mixed tokens use greatest non-whitespace byte overlap; ties choose first source occurrence. Fractional-byte attribution is retained per task. Helpers remain fully counted under their syntax categories, not double-counted as an overlapping category.',tiktoken_version=importlib.metadata.version('tiktoken'),density_sha256=hashlib.sha256(DENSITY.read_bytes()).hexdigest(),checks=checks,ranked=ranked,records=records)
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(checks=checks,ranked=ranked),indent=2))
if __name__=='__main__':main()
