"""Reference instruction-boundary liveness and reservations on historical inputs."""
import argparse,json,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;SUITE=HERE.parent;ROOT=SUITE.parent
p=argparse.ArgumentParser();p.add_argument('--helper',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.resolve().is_relative_to(ROOT):p.error('output outside git required')
results={}
with tempfile.TemporaryDirectory(prefix='nil-reference-control-') as d:
 folder=Path(d);raw=bytes(range(256))*65536;lines=b'alpha,beta,gamma\n'*1048576
 (folder/'bytes.bin').write_bytes(raw);(folder/'lines.bin').write_bytes(lines)
 for name,source,args,expected in [
  ('append',SUITE/'application/workloads/append.nil',['1048576'],1048576),
  ('scan',SUITE/'application/workloads/newlines.nil',[str(folder/'lines.bin')],1048576),
  ('transform',SUITE/'application/transform.nil',[str(folder/'bytes.bin'),str(folder/'transformed.bin')],16777216)]:
  r=subprocess.run([str(a.helper.resolve()),str(source),*args],cwd=folder,capture_output=True,timeout=1800)
  assert r.returncode==0 and r.stdout==f'{expected}\n'.encode(),(name,r.returncode,r.stdout,r.stderr)
  m=re.fullmatch(rb'NIL_REFERENCE_PROFILE live=(\d+) reservation=(\d+)\n',r.stderr);assert m,r.stderr
  if name=='transform':assert (folder/'transformed.bin').read_bytes()==bytes(255-x for x in raw)
  results[name]=dict(peak_instruction_boundary_live_bytes=int(m[1]),peak_quota_reservation_bytes=int(m[2]),limit_bytes=67108864,live_to_limit_ratio=int(m[1])/67108864,reservation_to_limit_ratio=int(m[2])/67108864)
  print(name,results[name],flush=True)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(dict(schema=1,method=__doc__,results=results),indent=2)+'\n')
