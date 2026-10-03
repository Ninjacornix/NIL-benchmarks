"""Executable byte contracts; deliberately independent of NIL loop implementations."""
from itertools import accumulate, groupby


def rows(data):
    if not data:
        return []
    parts = data.split(b'\n')
    return parts[:-1] if parts[-1] == b'' else parts


def decimals(values):
    return b''.join(str(value).encode('ascii') + b'\n' for value in values)


def expected(task, data, environment=None):
    if task in ('ascii_upper', 'ascii_lower', 'rot13', 'invert_bytes'):
        table = bytearray(range(256))
        for x in range(256):
            if task == 'ascii_upper' and 97 <= x <= 122:
                table[x] = x - 32
            elif task == 'ascii_lower' and 65 <= x <= 90:
                table[x] = x + 32
            elif task == 'rot13':
                if 65 <= x <= 90:
                    table[x] = 65 + (x - 65 + 13) % 26
                elif 97 <= x <= 122:
                    table[x] = 97 + (x - 97 + 13) % 26
            elif task == 'invert_bytes':
                table[x] = 255 - x
        return data.translate(bytes(table))
    if task == 'reverse_bytes':
        return bytes(reversed(data))
    if task == 'hex_encode':
        return ''.join(f'{x:02x}' for x in data).encode('ascii')
    if task == 'count_newlines':
        return decimals([sum(x == 10 for x in data)])
    if task == 'nonempty_lines':
        return b''.join(row + b'\n' for row in data.split(b'\n') if row)
    if task == 'normalize_crlf':
        return data.replace(b'\r\n', b'\n')
    if task == 'prefix_lines':
        return b'\n'.join(b'>' + row for row in rows(data)) + (b'\n' if data.endswith(b'\n') else b'')
    if task == 'first_fields_csv':
        return b''.join(row.partition(b',')[0] + b'\n' for row in rows(data))
    if task == 'sum_pairs':
        return decimals(sum(map(int, row.split(b','))) for row in rows(data))
    if task in ('sum_integers', 'buffer_sum'):
        return decimals([sum(map(int, rows(data)))])
    if task == 'min_max':
        values = sorted(map(int, rows(data)))
        return f'{values[0]},{values[-1]}\n'.encode('ascii')
    if task == 'dedupe_adjacent_lines':
        return b''.join(row + b'\n' for row, _ in groupby(rows(data)))
    if task == 'running_report':
        return b''.join(f'{i}:{sum(range(i+1))}\n'.encode('ascii') for i in range(int(data)))
    if task == 'number_lines':
        return b''.join(str(i).encode('ascii') + b':' + row + b'\n' for i, row in enumerate(rows(data), 1))
    if task == 'histogram_digits':
        return b''.join(f'{i}:{data.count(bytes([48+i]))}\n'.encode('ascii') for i in range(10))
    if task == 'buffer_dot':
        return decimals([sum(int(x) * int(y) for x, y in (row.split(b',') for row in rows(data)))])
    if task == 'prefix_sums':
        return decimals(accumulate(map(int, rows(data))))
    if task == 'copy_file':
        return data
    if task == 'slice_file':
        header, _, payload = data.partition(b'\n')
        start, length = map(int, header.split(b','))
        return payload[start:start + length]
    if task == 'expand_tabs':
        return b'    '.join(data.split(b'\t'))
    if task == 'env_lookup':
        return (environment or {}).get(data.decode('ascii'), '').encode('utf-8')
    raise ValueError(task)
