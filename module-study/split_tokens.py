"""Count real split bundles, separating reference spelling and manifest cost."""
import sys,json,argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'benchmarks/corpora/application-v5'))
from density import Vocabulary
import tiktoken
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
v=[Vocabulary(k,Path.home()/'.ollama/models') for k in ('gemma3_4b','qwen2.5_7b_instruct')]
e={k:tiktoken.get_encoding(k) for k in ('cl100k_base','o200k_base')}
def count(s):return {**{x.metadata['id']:len(x.ids(s)) for x in v},**{k:len(x.encode(s,disallowed_special=())) for k,x in e.items()}}
base=ROOT/'benchmarks/corpora/application-v5';bundle=base/'modules'
files=['count_newlines.nil','sum_integers.nil','reports.nil','reports.nil-module']
rows={f:count((bundle/f).read_text()) for f in files}
old={task:count((base/'programs'/task).read_text()) for task in files[:2]}
local_roots={f:count((bundle/f).read_text().replace('!plugin(7,0,','b(').replace('!plugin(7,1,','b(')) for f in files[:2]}
summary={}
for k in rows[files[0]]:
 original=sum(old[f][k] for f in files[:2]);roots=sum(rows[f][k] for f in files[:2]);shared=rows['reports.nil'][k];manifest=rows['reports.nil-module'][k]
 cross=roots-sum(local_roots[f][k] for f in files[:2])
 summary[k]={'original_two_programs':original,'split_roots':roots,'shared_source_once':shared,'cross_reference_overhead':cross,'sharing_and_refactor_delta':roots+shared-original-cross,'source_bundle_delta':roots+shared-original,'manifest_tokens':manifest,'complete_bundle_delta':roots+shared+manifest-original,'each_program_charged_full_library':{f:rows[f][k]+shared+manifest for f in files[:2]}}
report={'metric':'raw source tokens, not generation efficiency; sum token counts per file without special tokens','rows':rows,'original':old,'summary':summary,'tokenizers':[x.metadata for x in v]}
args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(summary,indent=2))
for x in v:x.close()
