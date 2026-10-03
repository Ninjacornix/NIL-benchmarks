"""Recount committed intermediate references; compare forecasts with verified density."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
from density import Vocabulary, MODELS
from external_suite import load_tasks

HERE = Path(__file__).resolve().parent
SUITE = HERE.parents[1]
BASELINE = '920e510'
SORT_ONLY = '6d36b83'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--density', type=Path, required=True)
    parser.add_argument('--attribution', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    measured = json.loads(args.density.read_text())
    prediction = json.loads((SUITE/'reports/2026-10-03/V5_ALGORITHMS_FORECAST.json').read_text())
    forecasts = {(r['task'], r['candidate']): r for r in prediction['records']}
    final = {(r['task'],r['language']): r for r in measured['records'] if r['status']=='verified'}
    import tiktoken
    vocabs = [Vocabulary(k, Path.home()/'.ollama/models') for k in MODELS]
    encs = {k:tiktoken.get_encoding(k) for k in ['cl100k_base','o200k_base']}
    def count(s):
        return {v.metadata['id']:len(v.ids(s)) for v in vocabs} | {k:len(e.encode(s,disallowed_special=())) for k,e in encs.items()}
    rows = []
    try:
        for task in load_tasks('external'):
            if task['nil_status']=='unsupported':
                continue
            ident = task['id']
            path = 'corpora/application-v5/programs/'+ident+'.nil'
            sources = [subprocess.check_output(['git','show',rev+':'+path],cwd=SUITE,text=True) for rev in [BASELINE,SORT_ONLY]]
            actual = (HERE/'programs'/ (ident+'.nil')).read_text()
            assert hashlib.sha256(actual.encode()).hexdigest()==final[ident,'expr-v5']['sha256']
            before, sorting = map(count,sources)
            after = final[ident,'expr-v5']['tokens']
            pred = forecasts[ident,'sort_each']
            assert before == pred['before']
            for key in before:
                rows.append({'task':ident,'tokenizer':key,'before':before[key],
                             'sort_only':sorting[key],'after':after[key],
                             'sort_predicted':forecasts[ident,'sort']['savings'][key],
                             'sort_actual':before[key]-sorting[key],
                             'each_marginal_predicted':pred['savings'][key]-forecasts[ident,'sort']['savings'][key],
                             'each_marginal_actual':sorting[key]-after[key],
                             'joint_actual':before[key]-after[key]})
        totals = {k:{field:sum(r[field] for r in rows if r['tokenizer']==k) for field in ['before','sort_only','after','sort_predicted','sort_actual','each_marginal_predicted','each_marginal_actual','joint_actual']} for k in (*MODELS,*encs)}
        old = json.loads((SUITE/'reports/2026-10-03/V5_ATTRIBUTION.json').read_text())
        new = json.loads(args.attribution.read_text())
        movement = {}
        for key in totals:
            previous={r['category']:r for r in old['ranked'][key]}
            current={r['category']:r for r in new['ranked'][key]}
            changes=[{'category':c,'integer_gap_before':previous[c]['difference'],'integer_gap_after':current[c]['difference'],
                      'integer_change':current[c]['difference']-previous[c]['difference'],
                      'fractional_gap_before':previous[c]['fractional_difference'],'fractional_gap_after':current[c]['fractional_difference'],
                      'fractional_change':str(Fraction(current[c]['fractional_difference'])-Fraction(previous[c]['fractional_difference']))} for c in previous]
            assert sum(r['integer_change'] for r in changes)==-totals[key]['joint_actual']
            assert sum(Fraction(r['fractional_change']) for r in changes)==-totals[key]['joint_actual']
            movement[key]=sorted(changes,key=lambda r:Fraction(r['fractional_change']))
        report={'schema':1,'baseline':BASELINE,'verified_sort_only_revision':SORT_ONLY,'tokenizers':measured['tokenizers'],
                'method':'Real tokenizer recount of frozen baseline/intermediate sources, verified final counts; intermediate sort-only external verification has 1790 checks. No inference. Original references and all baselines unchanged.',
                'totals':totals,'records':rows,'attribution_movement':movement,'exact_sum_checks':'passed'}
        args.output.write_text(json.dumps(report,indent=2)+'\n')
        print('PREDICTED_ACTUAL '+json.dumps(totals))
        print('ATTRIBUTION_MOVEMENT_EXACT_SUM_CHECKS passed')
    finally:
        for v in vocabs:v.close()


if __name__=='__main__':
    main()
