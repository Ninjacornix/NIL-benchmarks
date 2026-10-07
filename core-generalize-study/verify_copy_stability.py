"""Check repeated classification on the three programs exposing address reuse."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import copy_census

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / 'corpora/application-v5'))
from external_suite import load_goldens


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error('raw checks belong outside git')
    goldens = load_goldens()
    results = []
    for name in ['ex_binary_search_tree', 'ex_algo_graph_bfs', 'ex_algo_interval_merge']:
        source = HERE.parent / 'corpora/application-v5/programs' / (name + '.nil')
        samples = []
        for _ in range(3):
            with tempfile.TemporaryDirectory() as directory:
                work = Path(directory)
                rows = copy_census.run_pair(
                    ROOT / 'target/release/examples/application_check',
                    args.helper.resolve(), source, work,
                    bytes.fromhex(goldens[name]['input']), work / 'copies.tsv')
                assert (work / 'output.bin').read_bytes() == bytes.fromhex(goldens[name]['output'])
                # Allocation IDs and clocks are private; compare the causal ledger.
                samples.append([(r['kind'], r['bytes'], r['any_observation'],
                                 r['payload_observation']) for r in rows])
        assert samples[0] == samples[1] == samples[2], name
        results.append(dict(task=name, repeats=3, stable=True, events=len(samples[0]),
                            source_sha256=hashlib.sha256(source.read_bytes()).hexdigest()))
        print(name, '3 identical classification runs', len(samples[0]), 'events', flush=True)
    args.output.write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
