"""Join native physical events to future reference-semantic observations.

Unknown sites/roles/versions are errors, never implicitly AVOIDABLE. Completeness
of storage instrumentation is a separate prerequisite, not inferred by this join.
"""
import argparse,csv,json
from pathlib import Path

def read(path):
 with path.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def join(reference,native):
 sites={}
 for row in read(reference.with_suffix('.sites.tsv')):
  key=(int(row['site']),int(row['occurrence']));assert key not in sites,key
  sites[key]=(int(row['clock']),[int(v) for v in row['versions'].split(',')])
 versions={int(row['version']):(int(row['last_payload']),int(row['last_metadata'])) for row in read(reference.with_suffix('.versions.tsv'))}
 result=[]
 for row in read(native):
  key=(int(row['site']),int(row['occurrence']));assert key in sites,('unknown native site',row)
  clock,roles=sites[key];role=int(row['role']);assert 1<=role<=len(roles),('unknown operand role',row,roles)
  v=roles[role-1];assert v in versions,('unknown semantic source version',row,v)
  payload,metadata=versions[v];result.append({**row,'reference_clock':clock,'source_version':v,'any_observation':'REQUIRED' if max(payload,metadata)>clock else 'AVOIDABLE','payload_observation':'REQUIRED' if payload>clock else 'AVOIDABLE'})
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--native',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 result=join(a.reference,a.native);a.output.write_text(json.dumps({'coverage':'only instrumented events; storage coverage remains incomplete','events':result},indent=2)+'\n');print('JOINED',len(result),'copies')
if __name__=='__main__':main()
