"""Candidate census, not an ownership proof. Existing corpus sources stay frozen."""
import argparse,importlib.util,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve()
if out.is_relative_to(ROOT):p.error('results must stay outside checkout')
out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('suite',HERE.parent/'corpora/application-v5/external_suite.py');suite=importlib.util.module_from_spec(spec);spec.loader.exec_module(suite)
paths=[HERE.parent/'corpora/application-v5/programs'/(t['id']+'.nil') for t in suite.load_tasks() if t['nil_status']=='supported']
subprocess.run(['cargo','build','-p','nil-compiler','--locked','--offline'],cwd=ROOT,check=True)
rlib=max((ROOT/'target/debug/deps').glob('libnil_compiler-*.rlib'),key=lambda p:p.stat().st_mtime)
hir=max((ROOT/'target/debug/deps').glob('libnil_hir-*.rlib'),key=lambda p:p.stat().st_mtime)
bin=out/'census';subprocess.run(['rustc','--edition=2024',str(HERE/'copy_census.rs'),'--extern','nil_compiler='+str(rlib),'--extern','nil_hir='+str(hir),'-L','dependency='+str(ROOT/'target/debug/deps'),'-o',str(bin)],check=True)
# Three byte std instantiations and the unmodified insertion-sort source.
probe=out/'std-probe.nil';probe.write_text('=!fold(&b,!filter(&c,!map(&d,"abc")),0)\n2=a+b\n1:b=a>0\n1=a+1\n')
text=subprocess.check_output([str(bin),*map(str,paths),str(probe),str(ROOT/'benchmarks/hof-study/performance/sort.nil')],text=True)
rows=[]
for line in text.splitlines():
 path,calls,update_calls,update_functions,replacements=line.split('\t');rows.append(dict(source=path,calls=int(calls),sequence_update_callee_calls=int(update_calls),sequence_update_functions=int(update_functions),replacements=int(replacements)))
result={'method':'Direct calls to functions returning an owned value whose lineage includes a function parameter updated by Replace/Concat/Put/Insert, including nested fields and loops. Finite origin-set fixed point across calls. Does NOT prove physical aliasing, caller uniqueness, executed frequency, copying or safety of transfer.','corpus_programs':len(paths),'corpus_programs_with_candidates':sum(r['sequence_update_callee_calls']>0 for r in rows[:len(paths)]),'rows':rows}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
