"""Record actual DEV cost before held-out. Commit this output before the next run."""
import argparse
import hashlib
import json
from pathlib import Path
import time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--dev',type=Path,required=True);a=p.parse_args()
file=a.dev/'report.json';dev=json.loads(file.read_text());plan=json.loads((HERE/'experiment.json').read_text())
if dev['mock'] or dev['status']!='complete':raise ValueError('A successful real DEV run is required; do not forecast invented usage')
rows=[json.loads(x) for x in (a.dev/'attempts.jsonl').read_text().splitlines()]
if not rows or any(r.get('cost_usd') is None for r in rows):raise ValueError('Known DEV costs required')
mean=sum(r['cost_usd'] for r in rows)/len(rows);maximum=max(r['cost_usd'] for r in rows)
result=dict(cost_basis='notional subscription usage',model=plan['model'],effort=plan['effort'],dev_report_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
            timestamp_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),dev_requests=len(rows),dev_total_cost=dev['spent_usd'],
            mean_generation_request_cost=mean,max_observed_generation_request_cost=maximum,
            held_out_max_requests=min(432,plan['max_requests']-dev['config']['invocations']),remaining_cap=plan['spend_cap_usd']-dev['spent_usd'],
            per_attempt_output_cap=plan['per_attempt_output_cap'],trial_output_cap=plan['trial_output_cap'],
            worst_matrix_cost_at_dev_mean=min(432,plan['max_requests']-dev['config']['invocations'])*mean,worst_matrix_cost_at_dev_maximum=min(432,plan['max_requests']-dev['config']['invocations'])*maximum,
            warning='DEV is one task; held-out prompt/repair sizes can cost more. These are forecasts, not a safe hard bound. USD1 reservation and CLI/cumulative caps remain enforced.')
(HERE/'cost-forecast.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
