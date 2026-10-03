"""Pre-implementation whole-source token forecasts; writes no corpus sources.

Signature references and empty loop steps are deliberately INVALID in the frozen
compiler. These are counterfactual spellings, not verified reference solutions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from attribution import nil_labels
from density import Vocabulary, MODELS
from external_suite import load_tasks
from verify import HERE

HEADER = re.compile(r'(?:\([^\n]*?\)|\d+)?(?::(?:[isbvmt]|\d+))?=')


def function_name(index):
    result = ''
    index += 1
    while index:
        index, digit = divmod(index - 1, 26)
        result = chr(ord('a') + digit) + result
    return result


def signature_references(source):
    seen, result, changes = {}, [], []
    for index, line in enumerate(source.splitlines(keepends=True)):
        header = HEADER.match(line)
        assert header, line
        text = header.group()
        if text in seen:
            replacement = '^' + function_name(seen[text]) + '='
            # Select only syntactically longer headers; token acceptance is below.
            if len(replacement) < len(text):
                result.append(replacement + line[header.end():])
                changes.append({'function': index, 'reference': seen[text], 'before': text, 'after': replacement})
                continue
        seen.setdefault(text, index)
        result.append(line)
    return ''.join(result), changes


def empty_steps(source):
    _, structure = nil_labels(source)
    spans = structure['passthrough_spans']
    for start, end in reversed(spans):
        source = source[:start] + source[end:]
    return source, spans


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import tiktoken
    vocabs = [Vocabulary(key, Path.home() / '.ollama/models') for key in MODELS]
    encs = {key: tiktoken.get_encoding(key) for key in ('cl100k_base', 'o200k_base')}
    def counts(source):
        return {v.metadata['id']: len(v.ids(source)) for v in vocabs} | {key: len(enc.encode(source, disallowed_special=())) for key, enc in encs.items()}
    rows = []
    try:
        for task in load_tasks('external'):
            if task['nil_status'] == 'unsupported':
                continue
            source = (HERE / 'programs' / (task['id'] + '.nil')).read_text()
            before = counts(source)
            for name, change in [('signature_references', signature_references), ('empty_loop_steps', empty_steps)]:
                candidate, edits = change(source)
                after = counts(candidate)
                rows.append({'task': task['id'], 'candidate': name, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                             'before': before, 'after': after, 'savings': {k: before[k] - after[k] for k in before},
                             'edits': edits, 'counterfactual_source': candidate})
        totals = {name: {key: sum(r['savings'][key] for r in rows if r['candidate'] == name) for key in (*MODELS, *encs)} for name in ('signature_references', 'empty_loop_steps')}
        report = {'schema': 1, 'scope': '32 external paired tasks; original sources remain locked',
                  'warning': __doc__, 'selection_rule': 'same complete signature, earliest prior declaration, strictly shorter source header; no task selection',
                  'totals': totals, 'records': rows}
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / 'predictions.json').write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps(totals, indent=2))
    finally:
        for vocab in vocabs:
            vocab.close()


if __name__ == '__main__':
    main()
