


def calculate_level(total_gold_earned):
    level = [0, 500, 2000, 5000, 10000, 20000, 50000, 100000, 250000, 500000, 1000000]
    for i in range(len(level)-1, -1, -1):
        if total_gold_earned >= level[i]:
            return i
    return 0