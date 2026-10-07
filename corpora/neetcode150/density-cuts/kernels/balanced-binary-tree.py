def kernel(a, root):
    heights = [0] * len(a)
    stack = [(root, False)] if root != -1 else []
    okay = True
    while stack:
        i, ready = stack.pop()
        if not ready:
            stack.append((i, True))
            for child in a[i][1:]:
                if child != -1:
                    stack.append((child, False))
        else:
            lh = heights[a[i][1]] if a[i][1] != -1 else 0
            rh = heights[a[i][2]] if a[i][2] != -1 else 0
            okay &= abs(lh - rh) <= 1
            heights[i] = max(lh, rh) + 1
    return okay
