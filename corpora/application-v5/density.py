"""Raw source density; never creates an inference context or sends a model request."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

from verify import HERE, fingerprint
from external_suite import load_tasks

MODELS = {
    'gemma3_4b': ('gemma3/4b', 'a2af6cc3eb7fa8be8504abaf9b04e88f17a119ec3f04a3addf55f92841195f5a', 'aeda25e63ebd698fab8638ffb778e68bed908b960d39d0becc650fa981609d25'),
    'qwen2.5_7b_instruct': ('qwen2.5/7b-instruct', '845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e', '2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730'),
}


def file_hash(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


class Vocabulary:
    def __init__(self, key, model_home):
        import llama_cpp as lc
        self.lc = lc
        tag, manifest_hash, blob_hash = MODELS[key]
        manifest = model_home / 'manifests/registry.ollama.ai/library' / tag
        blob = model_home / 'blobs' / ('sha256-' + blob_hash)
        if file_hash(manifest) != manifest_hash or file_hash(blob) != blob_hash:
            raise ValueError(f'Pinned {key} asset mismatch')
        params = lc.llama_model_default_params()
        params.vocab_only = True
        params.n_gpu_layers = 0
        self.model = lc.llama_model_load_from_file(str(blob).encode(), params)
        if not self.model:
            raise RuntimeError(f'Cannot load {key} vocabulary')
        self.vocab = lc.llama_model_get_vocab(self.model)
        self.metadata = {'id': key, 'tag': tag, 'manifest_sha256': manifest_hash, 'gguf_sha256': blob_hash, 'vocabulary_size': lc.llama_vocab_n_tokens(self.vocab), 'backend': 'llama-cpp-python', 'backend_version': lc.__version__, 'vocab_only': True, 'add_special': False, 'parse_special': False}

    def ids(self, source):
        data = source.encode('utf-8')
        capacity = max(32, len(data) + 16)
        while True:
            tokens = (self.lc.llama_token * capacity)()
            count = self.lc.llama_tokenize(self.vocab, data, len(data), tokens, capacity, False, False)
            if count >= 0:
                return list(tokens[:count])
            capacity = -count

    def close(self):
        if self.model:
            self.lc.llama_model_free(self.model)
            self.model = None


def validate_verification(report):
    if report['source_hashes'] != fingerprint():
        raise ValueError('Verification stale: source or oracle changed; rerun verify.py')
    rows = report['results']
    if any(not row.get('semantic_ok', False) for row in rows if row.get('status') != 'unsupported'):
        raise ValueError('Unverified reference solution')
    return {(row['task'], row['language']): row for row in rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verification', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model-home', type=Path, default=Path.home() / '.ollama/models')
    args = parser.parse_args()
    from verify import SUITE, application
    output = args.output.expanduser().resolve()
    if output.is_relative_to(SUITE) or output.is_relative_to(application.ROOT):
        parser.error('Output must be outside source checkouts')
    verification = json.loads(args.verification.read_text())
    verified = validate_verification(verification)
    import tiktoken
    vocabularies = []
    try:
        for key in MODELS:
            vocabularies.append(Vocabulary(key, args.model_home.expanduser()))
        encodings = {name: tiktoken.get_encoding(name) for name in ['cl100k_base', 'o200k_base']}
        metadata = [v.metadata for v in vocabularies] + [{'id': name, 'backend': 'tiktoken', 'backend_version': tiktoken.__version__, 'add_special': False, 'parse_special': False, 'mergeable_ranks_sha256': hashlib.sha256(b''.join(len(piece).to_bytes(4, 'little') + piece + rank.to_bytes(4, 'little') for piece, rank in sorted(enc._mergeable_ranks.items(), key=lambda item: item[1]))).hexdigest()} for name, enc in encodings.items()]
        probes = ['(s,s)=!write(b,!read(a))\n', 'é\x00\n', '<eos><|endoftext|>', '']
        probe_ids = {v.metadata['id']: {text: v.ids(text) for text in probes} for v in vocabularies}
        probe_ids.update({name: {text: enc.encode(text, allowed_special=set(), disallowed_special=()) for text in probes} for name, enc in encodings.items()})
        # Existing paired asset is byte-identical to the pinned Qwen 7B JSON.
        sys.path.insert(0, str(SUITE / 'paired'))
        from run import verified_qwen_asset
        import tokenizers
        qwen_asset = verified_qwen_asset()
        qwen_reference = tokenizers.Tokenizer.from_file(str(qwen_asset))
        crosscheck = {'tokenizers_version': tokenizers.__version__, 'asset_sha256': file_hash(qwen_asset), 'official_model': 'Qwen/Qwen2.5-7B-Instruct', 'official_revision': 'a09a35458c702b33eeacc393d103063234e8bc28', 'comparisons': 0, 'mismatches': []}
        records = []
        tasks = load_tasks(verification.get('group', 'all'))
        for task in tasks:
            for language, extension in [('expr-v5', 'nil'), ('python', 'py'), ('cpp', 'cpp')]:
                verdict = verified[task['id'], language]
                if verdict.get('status') == 'unsupported':
                    records.append({'task': task['id'], 'language': language, 'status': 'unsupported'})
                    continue
                path = HERE / 'programs' / f"{task['id']}.{extension}"
                raw = path.read_bytes()
                source = raw.decode('utf-8')
                counts = {v.metadata['id']: len(v.ids(source)) for v in vocabularies}
                counts.update({name: len(enc.encode(source, allowed_special=set(), disallowed_special=())) for name, enc in encodings.items()})
                crosscheck['comparisons'] += 1
                if len(qwen_reference.encode(source, add_special_tokens=False).ids) != counts['qwen2.5_7b_instruct']:
                    crosscheck['mismatches'].append(task['id'] + '/' + language)
                records.append({'task': task['id'], 'category': task['category'], 'origin': task.get('origin', 'self-authored'), 'language': language, 'status': 'verified', 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'characters': len(source), 'tokens': counts})
        paired = [task['id'] for task in tasks if task['nil_status'] != 'unsupported']
        aggregates = {name: {language: sum(r['tokens'][name] for r in records if r['task'] in paired and r['language'] == language) for language in ['expr-v5', 'python', 'cpp']} for name in [v['id'] for v in metadata]}
        cuts = {'original': [t for t in tasks if not t['id'].startswith('ex_')],
                'new_external': [t for t in tasks if t['id'].startswith('ex_')],
                'combined': tasks}
        cut_aggregates = {}
        for label, selected in cuts.items():
            supported = [t['id'] for t in selected if t['nil_status'] != 'unsupported']
            cut_aggregates[label] = {
                'tasks': len(selected), 'paired_tasks': len(supported),
                'unsupported': len(selected) - len(supported),
                'tokens': {name: {language: sum(r['tokens'][name] for r in records
                            if r['status'] == 'verified' and r['task'] in supported and r['language'] == language)
                            for language in ['expr-v5', 'python', 'cpp']} for name in aggregates},
                'sizes': {language: {unit: sum(r[unit] for r in records if r['status'] == 'verified'
                          and r['task'] in supported and r['language'] == language)
                          for unit in ['bytes', 'characters']} for language in ['expr-v5', 'python', 'cpp']},
            }
        losses = {}
        for name in aggregates:
            indexed = {(r['task'], r['language']): r['tokens'][name] for r in records if r['status'] == 'verified'}
            losses[name] = {baseline: [{'task': task, 'nil': indexed[task, 'expr-v5'], 'baseline': indexed[task, baseline], 'outcome': 'tie' if indexed[task, 'expr-v5'] == indexed[task, baseline] else 'loss'} for task in paired if indexed[task, 'expr-v5'] >= indexed[task, baseline]] for baseline in ['python', 'cpp']}
        output.mkdir(parents=True, exist_ok=True)
        report = {'schema': 1, 'metric': 'raw source tokens; NOT tokens until correctness', 'python_version': sys.version.split()[0], 'compiler_revision': verification['compiler_revision'], 'source_hashes': fingerprint(), 'verification_sha256': file_hash(args.verification), 'tokenizers': metadata, 'probe_ids': probe_ids, 'qwen_crosscheck': crosscheck, 'measurement_script_sha256': file_hash(Path(__file__)), 'paired_tasks': paired, 'records': records, 'paired_aggregates': aggregates, 'cut_aggregates': cut_aggregates, 'nil_nonwins': losses}
        (output / 'density.json').write_text(json.dumps(report, indent=2) + '\n')
        with (output / 'tokens.csv').open('w', newline='') as stream:
            writer = csv.writer(stream, lineterminator='\n')
            writer.writerow(['task', 'language', 'tokenizer', 'status', 'bytes', 'characters', 'tokens', 'source_sha256'])
            for record in records:
                for tokenizer in metadata:
                    key = tokenizer['id']
                    writer.writerow([record['task'], record['language'], key, record['status'], record.get('bytes', ''), record.get('characters', ''), record.get('tokens', {}).get(key, ''), record.get('sha256', '')])
        from export import export
        exported = export(args.verification, output / 'adaptation.jsonl')
        print('Adaptation examples: ' + str(exported))
        print('Verified programs: ' + str(verification['totals']))
        print('QWEN_CROSSCHECK ' + json.dumps(crosscheck))
        print('PAIRED_TOTALS ' + json.dumps(aggregates))
        print('CUT_TOTALS ' + json.dumps(cut_aggregates))
        print('NONWINS ' + json.dumps(losses))
        print('Artifacts: ' + str(output))
    finally:
        for vocab in vocabularies:
            vocab.close()


if __name__ == '__main__':
    main()
