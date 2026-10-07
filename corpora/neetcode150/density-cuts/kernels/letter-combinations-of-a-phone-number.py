import itertools

def kernel(data):
    letters = [b'abc', b'def', b'ghi', b'jkl', b'mno', b'pqrs', b'tuv', b'wxyz']
    return [bytes(x) for x in itertools.product(*(letters[d - 50] for d in data))] if data else []
