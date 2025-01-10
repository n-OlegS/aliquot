def euclid(nums):
    a, b = sorted(nums)

    while b != 0:
        a, b = b, a % b
    return a


def backtrack_euc(a, b):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = backtrack_euc(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y
