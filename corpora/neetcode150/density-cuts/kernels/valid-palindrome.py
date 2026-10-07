def kernel(data):
    a = bytes((x + 32 if 65 <= x <= 90 else x for x in data if 48 <= x <= 57 or 65 <= x <= 90 or 97 <= x <= 122))
    return a == a[::-1]
