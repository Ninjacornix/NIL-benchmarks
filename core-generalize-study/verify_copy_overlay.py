"""Check trace classification and ordinary/native output parity on small adversaries.

This verifies implemented tracker paths, not full census coverage. No frozen task,
fixture, golden, or compiler checkout source is changed.
"""
import argparse,csv,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CASES=[
 ('live_old_sequence','(s,s)=x=!bytes(3,1);y=x[0:2];x[0]+y[0]', 'sequence_cow','REQUIRED','REQUIRED'),
 ('dead_old_sequence','(s,s)=x=!bytes(3,1);y=x[0:2];y[0]', None,None,None),
 ('old_length_only','(s,s)=x=!bytes(3,1);y=x[0:2];#x+y[0]', 'sequence_cow','REQUIRED','AVOIDABLE'),
 ('dead_slice_source','(s,s)=x=!bytes(3,1);y=!slice(x,0,2);y[0]', 'bytes_slice','AVOIDABLE','AVOIDABLE'),
 ('live_slice_source','(s,s)=x=!bytes(3,1);y=!slice(x,0,2);x[0]+y[0]', 'bytes_slice','REQUIRED','REQUIRED'),
 ('unselected_old_read','(s,s)=x=!bytes(3,1);y=x[0:2];(false?x[0]:0)+y[0]', 'sequence_cow','AVOIDABLE','AVOIDABLE'),
 ('selected_old_read','(s,s)=x=!bytes(3,1);y=x[0:2];(true?x[0]:0)+y[0]', 'sequence_cow','REQUIRED','REQUIRED'),
 ('returned_alias','(s,s)=x=!bytes(3,1);y=x[0:2];b(x)+y[0]\n(s)=a[0]', 'sequence_cow','REQUIRED','REQUIRED'),
 ('old_fixed_array','(s,s)=x=[1,1,1];y=x[0:2];x[0]+y[0]', 'array_update','REQUIRED','REQUIRED'),
 ('dead_fixed_array','(s,s)=x=[1,1,1];y=x[0:2];y[0]', 'array_update','AVOIDABLE','AVOIDABLE'),
 # Map ownership: the key argument payload is duplicated for insert/put, and the
 # map separately takes its own index and entry copies of that key.
 ('live_map_key_argument','(s,s)=k=!bytes(3,65);m=!insert(!map(),k,1);!get(m,k)+#k', 'map_key_argument','REQUIRED','REQUIRED'),
 ('dead_map_key_argument','(s,s)=k=!bytes(3,65);m=!insert(!map(),k,1);!size(m)', 'map_key_argument','AVOIDABLE','AVOIDABLE'),
 ('map_takes_own_index_key','(s,s)=k=!bytes(3,65);m=!insert(!map(),k,1);!size(m)', 'map_key_own_index','REQUIRED','REQUIRED'),
 ('map_takes_own_entry_key','(s,s)=k=!bytes(3,65);m=!insert(!map(),k,1);!size(m)', 'map_key_own_entry','REQUIRED','REQUIRED'),
 ('live_map_value_argument','(s,s)=v=!bytes(3,66);m=!insert(!bytemap(),!bytes(1,65),v);#!get(m,!bytes(1,65))+v[0]', 'map_value_argument','REQUIRED','REQUIRED'),
 ('metadata_map_value_argument','(s,s)=v=!bytes(3,66);m=!insert(!bytemap(),!bytes(1,65),v);#!get(m,!bytes(1,65))+#v', 'map_value_argument','REQUIRED','AVOIDABLE'),
 ('dead_map_value_argument','(s,s)=v=!bytes(3,66);m=!insert(!bytemap(),!bytes(1,65),v);!size(m)', 'map_value_argument','AVOIDABLE','AVOIDABLE'),
 ('map_value_materialization','(s,s)=m=!insert(!bytemap(),!bytes(1,65),!bytes(2,66));#!get(m,!bytes(1,65))', 'map_value_extract','AVOIDABLE','AVOIDABLE'),
]
def main():
 p=argparse.ArgumentParser();p.add_argument('--helper',type=Path,required=True);p.add_argument('--ordinary',type=Path,default=ROOT/'target/release/examples/core_check');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 if a.output.resolve().is_relative_to(ROOT):p.error('raw traces belong outside checkout')
 results=[]
 with tempfile.TemporaryDirectory(prefix='nil-copy-overlay-check-') as d:
  folder=Path(d);work=folder/'work';work.mkdir();trace=folder/'trace.tsv'
  for name,source,kind,any_expected,payload_expected in CASES:
   src=folder/'source.nil';src.write_text(source+'\n');(work/'input.bin').write_bytes(b'');env=os.environ.copy();env['NIL_COPY_TRACE_FILE']=str(trace)
   cmd=[str(src),'input.bin','output.bin','stdout.bin'];ordinary=subprocess.run([str(a.ordinary.resolve()),*cmd],cwd=work,capture_output=True,check=True);observed=subprocess.run([str(a.helper.resolve()),*cmd],cwd=work,env=env,capture_output=True,check=True)
   assert observed.stdout==ordinary.stdout and observed.stdout.startswith(b'VALUE\t'),(name,observed.stdout,ordinary.stdout)
   with trace.open() as f:events=list(csv.DictReader(f,delimiter='\t'))
   relevant=[e for e in events if e['kind']==kind]
   if kind:
    assert len(relevant)==1,(name,events)
    assert relevant[0]['any_observation']==any_expected and relevant[0]['payload_observation']==payload_expected,(name,relevant)
   else:assert not events,(name,events)
   value=observed.stdout.decode().split('\t')[1].strip()
   for opt in ['O0','O2']:
    binary=folder/'native';built=subprocess.run([str(a.ordinary.resolve()),str(src),'build-'+opt,str(binary)],cwd=work,capture_output=True,check=True);assert built.stdout==b'BUILD\tOK\n',(name,opt,built.stdout,built.stderr)
    run=subprocess.run([str(binary),'input.bin','output.bin'],cwd=work,capture_output=True,check=True);assert run.stdout==f'{value}\n'.encode() and not run.stderr,(name,opt,run.stdout,run.stderr)
   results.append({'name':name,'events':events,'reference_and_native_O0_O2':'pass'});print(name,'PASS',flush=True)
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'coverage':'partial tracker regression checks, not a complete census','results':results},indent=2)+'\n')
 print(f'TRACKER_CHECKS {len(results)} cases, {len(results)*2} native executions')
if __name__=='__main__':main()
