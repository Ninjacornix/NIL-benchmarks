"""Export verified authored positives; standard library only, no model access."""
import argparse
import json
from pathlib import Path

from verify import HERE, digest, fingerprint
from external_suite import load_tasks


def export(report_path, output):
    report = json.loads(report_path.read_text())
    if report['source_hashes'] != fingerprint():
        raise ValueError('Stale verification; rerun verify.py')
    verdicts = {(row['task'], row['language']): row for row in report['results']}
    tasks = load_tasks(report.get('group', 'all'))
    count = 0
    with output.open('w') as stream:
        for task in tasks:
            if task['nil_status'] == 'unsupported':
                continue
            verdict = verdicts[task['id'], 'expr-v5']
            if not verdict.get('semantic_ok') or verdict['native_tests_passed'] != 2 * verdict['tests_total']:
                raise ValueError('Unverified NIL completion')
            path = HERE / 'programs' / (task['id'] + '.nil')
            stream.write(json.dumps({'id': task['id'], 'profile': 'expr-v5', 'license': task.get('license', 'MIT'), 'origin': task.get('origin', 'self-authored'), 'provenance': task.get('provenance'), 'selected_property': task.get('selected_property'), 'prompt': task['prompt'], 'entry_contract': '(s,s)=...; file path parameters, return written byte count; no extra stdout', 'rationale': task['rationale'], 'completion': path.read_text(), 'source_sha256': digest(path), 'verification_sha256': digest(report_path), 'generation_study_overlap': task['adaptation_overlap']}, ensure_ascii=False) + '\n')
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verification', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    from verify import SUITE, application
    output = args.output.expanduser().resolve()
    if output.is_relative_to(SUITE) or output.is_relative_to(application.ROOT):
        parser.error('Export must be outside source checkouts')
    output.parent.mkdir(parents=True, exist_ok=True)
    print(f'Exported {export(args.verification, output)} verified NIL examples to {output}')


if __name__ == '__main__':
    main()
