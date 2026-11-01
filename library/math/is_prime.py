# ref: https://github.com/loop0919/loop0919-library/blob/main/library/math/is_prime.py


def is_prime(n: int) -> bool:
    """\
    Miller-Rabin 法で素数判定をする
    0 <= n <= 2**64 のときに判定可能

    Usage::

        print(is_prime(7))
        # => True

        print(is_prime(12))
        # => False
    """
    if n == 2:
        return True

    if n < 2 or (n & 1) == 0:
        return False

    n1 = n - 1
    d = n1
    s = 0

    while (d & 1) == 0:
        d //= 2
        s += 1

    for a in [2, 325, 9375, 28178, 450775, 9780504, 1795265022]:
        if a % n == 0:
            continue

        t = pow(a, d, n)

        if t == 1 or t == n1:
            continue

        for _ in range(s - 1):
            t = pow(t, 2, n)
            if t == n1:
                break
        else:
            return False

    return True
