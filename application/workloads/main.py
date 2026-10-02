import sys
mode = sys.argv[1]
if mode == 'newlines':
    with open(sys.argv[2], 'rb') as source:
        data = source.read()
    print(data.count(b'\n'))
else:
    n = int(sys.argv[2])
    if mode == 'reduce':
        data = [1] * n
        print(sum(data))
    elif mode == 'append':
        data = bytearray()
        for _ in range(n):
            data.append(120)
        print(len(data))
    elif mode == 'report':
        data = ''.join(f'{index}\n' for index in range(n)).encode()
        with open(sys.argv[3], 'wb') as output:
            output.write(data)
        print(len(data))
    else:
        raise ValueError(mode)
