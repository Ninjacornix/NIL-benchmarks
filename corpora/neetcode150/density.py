"""Complete standalone source screens, not model generation/repair measurements."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import tiktoken
HERE=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--verification',type=Path,required=True);args=ap.parse_args()
    verified={r['task']:r for r in json.loads(args.verification.read_text())['results'] if r.get('nil_status')=='verified'}
    rows=[];encodings={n:tiktoken.get_encoding(n) for n in ('cl100k_base','o200k_base')}
    for task in json.loads((HERE/'tasks.json').read_text())['tasks']:
        for language,ext in [('nil','nil'),('python','py'),('cpp','cpp')]:
            path=HERE/'programs'/(task['id']+'.'+ext)
            if not path.exists():continue
            data=path.read_bytes()
            if language=='nil' and (task['id'] not in verified or verified[task['id']]['nil_source_sha256']!=hashlib.sha256(data).hexdigest()):raise ValueError('NIL source has no matching successful verification: '+task['id'])
            text=data.decode();rows.append({'task':task['id'],'category':task['category'],'selected':task['selected'],'language':language,'source_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'characters':len(text),'tokens':{n:len(e.encode(text,allowed_special=set(),disallowed_special=())) for n,e in encodings.items()}})
    cohort={r['task'] for r in rows if r['language']=='nil'}
    totals={}
    for language in ('nil','python','cpp'):
        group=[r for r in rows if r['language']==language and r['task'] in cohort]
        totals[language]={'programs':len(group),'bytes':sum(r['bytes'] for r in group),'characters':sum(r['characters'] for r in group),'tokens':{n:sum(r['tokens'][n] for r in group) for n in encodings}}
    result={'schema':1,'verification_sha256':hashlib.sha256(args.verification.read_bytes()).hexdigest(),'metric':'Standalone source counts; includes all I/O drivers/helpers. Density is not failure-inclusive model tokens to a correct program. Only verified-NIL cohort is paired; failed/unattempted tasks are not silently counted as zero.','tokenizer_version':importlib.metadata.version('tiktoken'),'tokenizers':{n:{'vocabulary':e.n_vocab,'mergeable_ranks_sha256':hashlib.sha256(b''.join(k+str(v).encode()+b'\n' for k,v in sorted(e._mergeable_ranks.items()))).hexdigest()} for n,e in encodings.items()},'cohort_tasks':sorted(cohort),'totals':totals,'per_task':rows}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'verified_nil':len(cohort),'tokenizer_version':result['tokenizer_version'],'paired_totals':totals},indent=2))
if __name__=='__main__':main()
