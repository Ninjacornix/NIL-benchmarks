def kernel(a, lo, hi):
    lo, hi = (lo, hi)
    out = []
    inserted = False
    for x, y in a:
        if y < lo:
            out.append((x, y))
        elif x > hi:
            if not inserted:
                out.append((lo, hi))
                inserted = True
            out.append((x, y))
        else:
            lo = min(lo, x)
            hi = max(hi, y)
    if not inserted:
        out.append((lo, hi))
    return out
