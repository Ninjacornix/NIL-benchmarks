"""Reference liveness and prospective reservations; frozen largest fixtures only."""
import argparse,hashlib,json,re,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;SUITE=HERE.parent;ROOT=SUITE.parent
sys.path.insert(0,str(SUITE/'corpora/neetcode150'))
import fixtures,reference

def main():
 p=argparse.ArgumentParser();p.add_argument('--helper',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.resolve().is_relative_to(ROOT):p.error('raw profiles belong outside git')
 tasks=json.loads((SUITE/'corpora/neetcode150/tasks.json').read_text())['tasks'];golden=json.loads((SUITE/'corpora/neetcode150/goldens.json').read_text());cohort=json.loads((HERE/'NATURAL.json').read_text());results=[]
 a.output.parent.mkdir(parents=True,exist_ok=True);progress=a.output.with_suffix('.jsonl');progress.write_text('')
 for row in cohort['tasks']:
  slug=row['task'];task=next(t for t in tasks if t['id']==slug);name,data=list(fixtures.cases(task))[-1];answer=reference.SOLVERS[slug](data)
  assert hashlib.sha256(data).hexdigest()==golden[slug][name]['input_sha256'] and hashlib.sha256(answer).hexdigest()==golden[slug][name]['output_sha256']
  result={'task':slug,'profiles':{}}
  for mode,source in [('natural',HERE/'natural'/f'{slug}.nil'),('tuned',SUITE/'corpora/neetcode150/programs'/f'{slug}.nil')]:
   assert hashlib.sha256(source.read_bytes()).hexdigest()==row[mode+'_sha256']
   with tempfile.TemporaryDirectory(prefix='nil-reference-memory-') as folder:
    work=Path(folder);(work/'input.bin').write_bytes(data)
    r=subprocess.run([str(a.helper.resolve()),str(source),'input.bin','output.bin','stdout.bin'],cwd=work,capture_output=True,timeout=120)
    assert r.returncode==0 and r.stdout==f'VALUE\t{len(answer)}\n'.encode() and (work/'output.bin').read_bytes()==answer and (work/'stdout.bin').read_bytes()==b'' and (work/'input.bin').read_bytes()==data,(slug,mode,r.returncode,r.stdout,r.stderr)
    m=re.fullmatch(rb'NIL_REFERENCE_PROFILE live=(\d+) reservation=(\d+)\n',r.stderr);assert m,r.stderr
    result['profiles'][mode]={'source_sha256':row[mode+'_sha256'],'peak_semantic_live_bytes':int(m[1]),'peak_quota_reservation_bytes':int(m[2]),'limit_bytes':67108864,'semantic_live_to_limit_ratio':int(m[1])/67108864,'reservation_to_limit_ratio':int(m[2])/67108864}
  results.append(result)
  with progress.open('a') as f:f.write(json.dumps(result)+'\n')
  print(slug,result['profiles'],flush=True)
 a.output.write_text(json.dumps(dict(schema=1,method=__doc__,helper_manifest=json.loads((a.helper.resolve().parents[3]/'MANIFEST.json').read_text()),results=results),indent=2)+'\n')
if __name__=='__main__':main()
