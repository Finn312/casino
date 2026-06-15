def calculate_multiplier(bombs, revealed):
    p = 1.0
    for i in range(revealed):
        p *= (25 - bombs - i) / (25 - i)
    return round((1 / p) * 0.97, 2)