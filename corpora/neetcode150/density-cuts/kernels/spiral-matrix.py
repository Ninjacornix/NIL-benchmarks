def kernel(r, c, a):
    r, c = (r, c)
    out = []
    top, left, bottom, right = (0, 0, r, c)
    while top < bottom and left < right:
        out.extend(a[top][left:right])
        top += 1
        out.extend((a[i][right - 1] for i in range(top, bottom)))
        right -= 1
        if top < bottom:
            out.extend(reversed(a[bottom - 1][left:right]))
            bottom -= 1
        if left < right:
            out.extend((a[i][left] for i in range(bottom - 1, top - 1, -1)))
            left += 1
    return out
