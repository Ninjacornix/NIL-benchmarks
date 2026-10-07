def kernel(gas, costs):
    prefix = 0
    low = 0
    start = 0
    for i, (g, c) in enumerate(zip(gas, costs)):
        prefix += g - c
        if prefix < low:
            low = prefix
            start = i + 1
    return start if gas and prefix >= 0 else -1
