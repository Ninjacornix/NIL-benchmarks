"""Exhaustive source-token ledger, not a causal estimate of language changes.

Only the fractional cl100k ledger drives ranking; the same labels are applied to four real
vocabularies. Token byte pieces reconstruct the source exactly (Gemma adds one
synthetic leading space). Mixed-category tokens get their greatest non-whitespace
byte overlap, with ties resolved by first source occurrence. A fractional-byte
ledger is also retained to expose sensitivity to that choice.
"""
import argparse
import ast
from collections import Counter
import ctypes
from fractions import Fraction
import hashlib
import io
import json
import re
import token
import tokenize
from pathlib import Path

from density import Vocabulary, MODELS
from external_suite import load_tasks
from verify import HERE

CATEGORIES = ('signature', 'loop_delimiters', 'unchanged_state', 'loop_index_bound',
              'intrinsic_name', 'call_identifier', 'identifier', 'operator',
              'numeric_literal', 'text_literal', 'boolean_literal', 'separator', 'keyword', 'comment', 'whitespace')
NIL_LEX = re.compile(r'"(?:\\.|[^"\\])*"|![a-z]+|\d+|[a-z]+|==|!=|<=|>=|\s+|.', re.S)


def paint(labels, start, end, category):
    labels[start:end] = [category] * (end - start)


def lexical_nil(source):
    labels = ['unclassified'] * len(source)
    for match in NIL_LEX.finditer(source):
        text = match.group()
        if text.isspace():
            category = 'whitespace'
        elif text.startswith('"'):
            category = 'text_literal'
        elif text.isdecimal():
            category = 'numeric_literal'
        elif text in ('true', 'false'):
            category = 'boolean_literal'
        elif text.startswith('!'):
            category = 'intrinsic_name'
        elif text.isalpha():
            category = 'call_identifier' if source[match.end():].lstrip().startswith('(') else 'identifier'
        elif text in ('+', '-', '*', '/', '%', '#', '==', '!=', '<', '>', '<=', '>=', '?', ':', '='):
            category = 'operator'
        else:
            category = 'separator'
        paint(labels, match.start(), match.end(), category)
    return labels


def pairs(source):
    stack, closing = [], {}
    for match in NIL_LEX.finditer(source):
        text = match.group()
        if text in ('(', '['):
            stack.append((text, match.start()))
        elif text in (')', ']'):
            opening, start = stack.pop()
            assert (opening, text) in (('(', ')'), ('[', ']'))
            closing[start] = match.start()
    assert not stack
    return closing


def split_top(source, start, end, delimiter, closing):
    spans, begin, cursor = [], start, start
    # Lexical iteration excludes quoted delimiters and jumps balanced expressions.
    for match in NIL_LEX.finditer(source, start, end):
        if match.start() < cursor:
            continue
        if match.start() in closing:
            cursor = closing[match.start()] + 1
        elif match.group() == delimiter:
            spans.append((begin, match.start()))
            begin = match.end()
    return spans + [(begin, end)]


def nil_labels(source):
    labels = lexical_nil(source)
    closing = pairs(source)
    loops, passthrough = [], []
    # All corpus declarations occupy one line. Fail rather than misclassify a new layout.
    for line in re.finditer(r'[^\n]+', source):
        header = re.match(r'(?:\([^\n]*?\)|\d+)(?::(?:[isbvmt]|\d+))?=', line.group())
        if not header:
            raise ValueError('Unsupported NIL declaration layout: ' + line.group())
        paint(labels, line.start(), line.start() + header.end(), 'signature')
    for match in NIL_LEX.finditer(source):
        if match.group() != '@':
            continue
        opening = match.end()
        assert source[opening] == '('
        end = closing[opening]
        sections = split_top(source, opening + 1, end, ';', closing)
        assert len(sections) == 4
        steps = split_top(source, *sections[2], ',', closing)
        initials = split_top(source, *sections[0], ',', closing)
        assert len(steps) == len(initials)
        for point in (match.start(), opening, end, *(part[1] for part in sections[:-1])):
            paint(labels, point, point + 1, 'loop_delimiters')
        condition = source[slice(*sections[1])]
        for index, (start, stop) in enumerate(steps):
            name = chr(ord('a') + index)
            step = source[start:stop].strip()
            if step == name:
                paint(labels, start, stop, 'unchanged_state')
                passthrough.append([start, stop])
            elif step in (name + '+1', name + '-1') and re.search(r'\b' + name + r'\b', condition):
                paint(labels, start, stop, 'loop_index_bound')
        # A scalar comparison serving only as the loop condition is scaffolding;
        # complex predicates remain lexically attributed, not presumed removable.
        if re.fullmatch(r'[a-z](?:<|<=|>|>=)(?:#[a-z]|[a-z]|\d+)', condition):
            paint(labels, *sections[1], 'loop_index_bound')
        loops.append({'start': match.start(), 'end': end + 1, 'state_count': len(steps)})
    return labels, {'loops': loops, 'passthrough_spans': passthrough}


def python_labels(source):
    labels = ['whitespace'] * len(source)
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    def at(position):
        row, column = position
        return offsets[row - 1] + column
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    for item in tokens:
        start, end = at(item.start), at(item.end)
        if item.type == token.STRING:
            category = 'text_literal'
        elif item.type == token.NUMBER:
            category = 'numeric_literal'
        elif item.string in ('True', 'False'):
            category = 'boolean_literal'
        elif item.type == token.COMMENT:
            category = 'comment'
        elif item.type == token.NAME:
            import keyword
            category = 'keyword' if keyword.iskeyword(item.string) else 'identifier'
            if category == 'identifier' and source[end:].lstrip().startswith('('):
                category = 'call_identifier'
        elif item.type == token.OP:
            category = 'separator' if item.string in '()[]{},;:.' else 'operator'
        else:
            continue
        paint(labels, start, end, category)
    tree = ast.parse(source)
    local_functions = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called = node.func
            if isinstance(called, ast.Name) and called.id not in local_functions:
                paint(labels, at((called.lineno, called.col_offset)), at((called.end_lineno, called.end_col_offset)), 'intrinsic_name')
            elif isinstance(called, ast.Attribute):
                end = at((called.end_lineno, called.end_col_offset))
                paint(labels, end - len(called.attr), end, 'intrinsic_name')
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = at((node.lineno, node.col_offset))
            opening = next(t for t in tokens if at(t.start) >= start and t.string == '(')
            depth = 0
            for t in tokens:
                if at(t.start) < at(opening.start):
                    continue
                depth += t.string == '('
                depth -= t.string == ')'
                if t.string == ':' and depth == 0:
                    paint(labels, start, at(t.end), 'signature')
                    break
        elif isinstance(node, (ast.For, ast.While)):
            start = at((node.lineno, node.col_offset))
            paint(labels, start, start + (3 if isinstance(node, ast.For) else 5), 'loop_delimiters')
            if isinstance(node, ast.While):
                predicate = node.test
                if isinstance(predicate, ast.Compare):
                    paint(labels, at((predicate.lineno, predicate.col_offset)),
                          at((predicate.end_lineno, predicate.end_col_offset)), 'loop_index_bound')
            elif isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                paint(labels, at((node.target.lineno, node.target.col_offset)),
                      at((node.iter.end_lineno, node.iter.end_col_offset)), 'loop_index_bound')
    return labels, {}


def pieces(vocabulary, ids):
    result = []
    for tid in ids:
        capacity = 256
        while True:
            buffer = ctypes.create_string_buffer(capacity)
            count = vocabulary.lc.llama_token_to_piece(vocabulary.vocab, tid, buffer, capacity, 0, False)
            if count >= 0:
                result.append(buffer.raw[:count])
                break
            capacity = -count
    return result


def ledger(source, labels, token_pieces, synthetic_prefix=False):
    data = source.encode()
    assert len(data) == len(source), 'ASCII ledger required; use byte-offset labels for non-ASCII'
    joined = b''.join(token_pieces)
    if synthetic_prefix:
        assert joined == b' ' + data
        token_pieces = [token_pieces[0][1:]] + token_pieces[1:]
    else:
        assert joined == data
    totals, fractions, rows = Counter(), Counter(), []
    cursor = 0
    for index, piece in enumerate(token_pieces):
        span = labels[cursor:cursor + len(piece)]
        meaningful = [label for label, byte in zip(span, piece) if not chr(byte).isspace()]
        voting = meaningful or span
        assert voting, 'Empty source token'
        weights = Counter(voting)
        category = max(weights, key=weights.get)  # Counter preserves first occurrence for ties.
        totals[category] += 1
        for key, count in weights.items():
            fractions[key] += Fraction(count, len(voting))
        rows.append({'index': index, 'start': cursor, 'end': cursor + len(piece),
                     'piece_hex': piece.hex(), 'category': category,
                     'byte_votes': dict(weights)})
        cursor += len(piece)
    assert cursor == len(data)
    assert sum(totals.values()) == len(token_pieces)
    assert sum(fractions.values()) == len(token_pieces)
    assert set(totals) <= set(CATEGORIES)
    return dict(totals), {k: str(v) for k, v in fractions.items()}, rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--density', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import tiktoken
    frozen = json.loads(args.density.read_text())
    records = {(r['task'], r['language']): r for r in frozen['records'] if r['status'] == 'verified'}
    tasks = [t for t in load_tasks('external') if t['nil_status'] != 'unsupported']
    vocabularies = [Vocabulary(key, Path.home() / '.ollama/models') for key in MODELS]
    encodings = {key: tiktoken.get_encoding(key) for key in ('cl100k_base', 'o200k_base')}
    totals = {name: {lang: Counter() for lang in ('expr-v5', 'python')} for name in (*MODELS, *encodings)}
    fractional = {name: {lang: Counter() for lang in ('expr-v5', 'python')} for name in totals}
    all_rows, structures = [], {}
    try:
        for task in tasks:
            for lang, ext in (('expr-v5', 'nil'), ('python', 'py')):
                path = HERE / 'programs' / (task['id'] + '.' + ext)
                raw = path.read_bytes()
                assert hashlib.sha256(raw).hexdigest() == records[task['id'], lang]['sha256']
                source = raw.decode()
                labels, structure = nil_labels(source) if lang == 'expr-v5' else python_labels(source)
                structures[task['id'] + '/' + lang] = structure
                streams = {v.metadata['id']: pieces(v, v.ids(source)) for v in vocabularies}
                streams.update({name: [enc.decode_single_token_bytes(tid) for tid in enc.encode(source, disallowed_special=())] for name, enc in encodings.items()})
                for name, stream in streams.items():
                    counts, shares, rows = ledger(source, labels, stream, name == 'gemma3_4b')
                    assert sum(counts.values()) == records[task['id'], lang]['tokens'][name]
                    totals[name][lang].update(counts)
                    fractional[name][lang].update({k: Fraction(v) for k, v in shares.items()})
                    all_rows.append({'task': task['id'], 'language': lang, 'tokenizer': name,
                                     'categories': counts, 'fractional': shares, 'tokens': rows})
        ranked = {}
        for name, languages in totals.items():
            rows = [{'category': c, 'nil': languages['expr-v5'][c], 'python': languages['python'][c],
                     'difference': languages['expr-v5'][c] - languages['python'][c],
                     'fractional_difference': str(fractional[name]['expr-v5'][c] - fractional[name]['python'][c])} for c in CATEGORIES]
            expected = frozen['cut_aggregates']['new_external']['tokens'][name]
            assert sum(r['difference'] for r in rows) == expected['expr-v5'] - expected['python']
            assert sum(Fraction(r['fractional_difference']) for r in rows) == expected['expr-v5'] - expected['python']
            ranked[name] = sorted(rows, key=lambda r: -Fraction(r['fractional_difference']))
        args.output.mkdir(parents=True, exist_ok=True)
        report = {'schema': 1, 'scope': '32 external paired tasks; immutable current source hashes',
                  'method': __doc__, 'source_density_sha256': hashlib.sha256(args.density.read_bytes()).hexdigest(),
                  'tokenizers': frozen['tokenizers'], 'categories': CATEGORIES, 'ranked': ranked,
                  'structures': structures, 'records': all_rows,
                  'source_hashes': frozen['source_hashes'],
                  'analysis_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        (args.output / 'ledger.json').write_text(json.dumps(report, indent=2) + '\n')
        summary = {k: v for k, v in report.items() if k != 'records'}
        summary['records'] = [{k: v for k, v in row.items() if k != 'tokens'} for row in all_rows]
        summary['raw_ledger'] = 'Regenerate ledger.json for every token offset, piece and byte vote.'
        (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        print(json.dumps(ranked, indent=2))
        print('ACCOUNTED ' + json.dumps({'source_files': 2 * len(tasks), 'tokenizer_streams': len(all_rows), 'tokens': sum(sum(r['categories'].values()) for r in all_rows), 'exact_sum_checks': 'passed'}))
    finally:
        for v in vocabularies:
            v.close()


if __name__ == '__main__':
    main()
