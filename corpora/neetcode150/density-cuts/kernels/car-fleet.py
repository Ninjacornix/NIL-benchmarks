def kernel(target, a):
    a.sort(reverse=True)
    fleets = 0
    numerator = 0
    denominator = 1
    for pos, speed in a:
        distance = target - pos
        if distance * denominator > numerator * speed:
            fleets += 1
            numerator = distance
            denominator = speed
    return fleets
