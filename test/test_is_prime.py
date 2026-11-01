import random
from math import isqrt

import pytest
from sympy import isprime as sympy_isprime
from sympy import nextprime

from library.math.is_prime import is_prime

# 実装で使っている Miller-Rabin の基数
BASES = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]


def naive_is_prime(n: int) -> bool:
    """試し割りで素数判定する"""
    return n >= 2 and all(n % i != 0 for i in range(2, isqrt(n) + 1))


def sieve(n: int) -> list[bool]:
    """エラトステネスの篩で 0 以上 n 未満の素数表を作る"""
    table = [True] * n
    table[0] = table[1] = False
    for i in range(2, isqrt(n - 1) + 1):
        if table[i]:
            for j in range(i * i, n, i):
                table[j] = False
    return table


def test_docstring_example():
    assert is_prime(7)
    assert not is_prime(12)


def test_matches_sieve():
    limit = 10**5
    table = sieve(limit)
    assert [n for n in range(limit) if is_prime(n) != table[n]] == []


@pytest.mark.parametrize("n", [-1, -2, -7, -(2**61 - 1)])
def test_negative(n):
    assert not is_prime(n)


@pytest.mark.parametrize(
    "n",
    [
        998244353,
        10**9 + 7,
        4294967279,
        4294967291,  # 2**32 未満で最大の素数
        2**61 - 1,
        18446744073709551557,  # 2**64 未満で最大の素数
    ],
)
def test_large_prime(n):
    assert is_prime(n)


@pytest.mark.parametrize(
    "n",
    [
        561,  # カーマイケル数
        2047,  # 底 2 の強擬素数
        1373653,  # 底 2, 3 の強擬素数
        3215031751,  # 底 2, 3, 5, 7 の強擬素数
        3825123056546413051,  # 底 2, 3, 5, ..., 23 の強擬素数
        4294967279 * 4294967291,  # 大きい素数 2 つの積
        4294967291**2,  # 大きい素数の 2 乗
        2**64 - 1,
        2**64,
    ],
)
def test_large_composite(n):
    assert not is_prime(n)


@pytest.mark.parametrize("a", BASES)
def test_divisors_of_bases(a):
    # n が基数 a の約数だと a % n == 0 になり、その基数での判定を飛ばす
    divisors = {d for i in range(1, isqrt(a) + 1) if a % i == 0 for d in (i, a // i)}
    for d in sorted(divisors):
        assert is_prime(d) == naive_is_prime(d), d


@pytest.mark.parametrize("seed", range(5))
def test_random_64bit(seed):
    # sympy の isprime は 2**64 未満なら確定的に正しい
    rng = random.Random(seed)
    for _ in range(200):
        n = rng.randrange(2**64)
        assert is_prime(n) == sympy_isprime(n), n


@pytest.mark.parametrize("seed", range(5))
def test_random_semiprime(seed):
    # 32 bit 程度の素数 2 つの積は、小さい素因数を持たないので判定が難しい
    rng = random.Random(seed)
    for _ in range(50):
        p = nextprime(rng.randrange(2**31, 2**32))
        q = nextprime(rng.randrange(2**31, 2**32))
        assert is_prime(p)
        assert is_prime(q)
        assert not is_prime(p * q), (p, q)
