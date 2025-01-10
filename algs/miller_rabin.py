import random


def miller_rabin(n, t):
    if n in [1, 2, 3]:
        return True
    elif n == 4:
        return False

    r, s = 0, n - 1

    while s // 2 == 0:
        s //= 2
        r += 1

    for _ in range(t):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)

        if x == 1 or x == (n - 1):
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True
