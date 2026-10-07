"""Three separately reported cuts; accept only oracle-verified copied programs."""
import argparse,hashlib,importlib.metadata,json,subprocess
from pathlib import Path
import tiktoken
HERE=Path(__file__).resolve().parent
CORPUS=HERE.parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--verification',type=Path,required=True);p.add_argument('--cohort-verification',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 checked=json.loads(a.verification.read_text());cohort=json.loads(a.cohort_verification.read_text())
 assert checked['tasks']==29 and all(r['pass'] for r in checked['results'])
 assert cohort['totals']['verified_nil']==29 and cohort['totals']['checks']==cohort['totals']['passed_checks']
 enc={n:tiktoken.get_encoding(n) for n in ['cl100k_base','o200k_base']};rows=[]
 for task in sorted(r['task'] for r in checked['results']):
  for cut in ['full-program','kernel-only','minimal-io']:
   for lang,ext in [('nil','nil'),('python','py'),('cpp','cpp')]:
    folder=CORPUS/'programs' if cut=='full-program' else HERE/('kernels' if cut=='kernel-only' else cut)
    source=folder/(task+'.'+ext);data=source.read_bytes();text=data.decode();sha=hashlib.sha256(data).hexdigest()
    v=next(r for r in checked['results'] if r['task']==task)
    if cut=='minimal-io':assert sha==v['hashes']['minimal-io/'+lang]
    if cut=='full-program' and lang=='nil':assert sha==next(r for r in cohort['results'] if r['task']==task)['nil_source_sha256']
    row={'cut':cut,'task':task,'language':lang,'sha256':sha,'bytes':len(data),'characters':len(text),'tokens':{n:len(e.encode(text,disallowed_special=())) for n,e in enc.items()}}
    if cut=='full-program' and lang=='nil':
     old=subprocess.check_output(['git','show','6fd268d:corpora/neetcode150/programs/'+task+'.nil'],cwd=CORPUS)
     row['before_tokens']={n:len(e.encode(old.decode(),disallowed_special=())) for n,e in enc.items()};row['token_delta']={n:row['tokens'][n]-row['before_tokens'][n] for n in enc}
    rows.append(row)
 totals={}
 for cut in ['full-program','kernel-only','minimal-io']:
  totals[cut]={}
  for lang in ['nil','python','cpp']:
   selected=[r for r in rows if r['cut']==cut and r['language']==lang]
   totals[cut][lang]={k:sum(r[k] for r in selected) for k in ['bytes','characters']}
   totals[cut][lang]['tokens']={n:sum(r['tokens'][n] for r in selected) for n in enc}
  totals[cut]['nil_gap']={n:{lang:totals[cut]['nil']['tokens'][n]/totals[cut][lang]['tokens'][n]-1 for lang in ['python','cpp']} for n in enc}
 result={'schema':1,'cohort':29,'metric':'Source density, not failure-inclusive generation/repair tokens. Typed kernels include every algorithm helper, signature and required type/import declaration; adapters excluded in every language. NIL retains flat-buffer input-layout arithmetic. Standalone full programs retain all historical driver costs. Minimal-I/O baseline copies are idiomatic iterator/stream adapters; NIL keeps its already compact original I/O. Kernel-host copies verify typed-result reconstruction on unchanged fixtures.','tiktoken_version':importlib.metadata.version('tiktoken'),'verification_sha256':hashlib.sha256(a.verification.read_bytes()).hexdigest(),'totals':totals,'per_task':rows}
 a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
