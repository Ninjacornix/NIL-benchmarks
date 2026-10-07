def kernel(a, root):
    stack = []
    current = root
    previous = None
    while current != -1 or stack:
        while current != -1:
            stack.append(current)
            current = a[current][1]
        current = stack.pop()
        value = a[current][0]
        if previous is not None and value <= previous:
            return False
        previous = value
        current = a[current][2]
    return True
