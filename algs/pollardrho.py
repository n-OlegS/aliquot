import random

from algs.euclidan_alg import euclid
from algs.miller_rabin import miller_rabin


def f(x, addend, n):
    return pow(x, 2, n) + addend


def single_factor(n, prime_check=True):
    if prime_check:
        if miller_rabin(n, 20):
            return n

    x = random.randint(2, n - 2) % n
    y = x
    add = random.randint(0, 2)
    d = 1

    while d == 1:
        x = f(x, add, n)
        y = f(f(y, add, n), add, n)
        d = euclid([abs(x - y), n])

        if d == n:
            return single_factor(n)

    return d


def rho_factorize(n, prime_check=True):
    doubles = [1]

    while n % 2 == 0:
        doubles.append(doubles[-1] * 2)
        n //= 2

    factors = [1, n]

    if n == 1:
        factors = [1]
    else:
        factor = single_factor(n, prime_check=prime_check)

        if factor != n:
            # factors += rho_factorize(factor) + rho_factorize(n // factor)
            to_add = []
            for i in rho_factorize(factor):
                for j in rho_factorize(n // factor):
                    to_add.append(i * j)

            factors += list(set(to_add))

    old_factors = list(set(factors))
    factors = []

    for double in doubles:
        for f in old_factors:
            factors.append(f * double)

    return list(set(factors))
