import itertools

def letter_combinations_of_a_phone_number(data):
    letters=[b'abc',b'def',b'ghi',b'jkl',b'mno',b'pqrs',b'tuv',b'wxyz']
    return b''.join(bytes(x)+b'\n' for x in itertools.product(*(letters[d-50] for d in data))) if data else b''

if __name__ == '__main__':
    import sys
    from pathlib import Path
    answer = letter_combinations_of_a_phone_number(Path(sys.argv[1]).read_bytes())
    Path(sys.argv[2]).write_bytes(answer)
    print(len(answer))
