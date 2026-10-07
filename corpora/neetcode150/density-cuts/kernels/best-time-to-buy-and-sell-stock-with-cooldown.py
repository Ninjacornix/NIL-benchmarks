def kernel(a):
    hold = -10 ** 18
    sold = -10 ** 18
    rest = 0
    for price in a:
        hold, sold, rest = (max(hold, rest - price), hold + price, max(rest, sold))
    return max(rest, sold)
