import math
import random
from functools import cmp_to_key

import pytest

from library.geometry.arg_cmp import arg_cmp
from library.misc.cmp_sort import cmp_sort


def sign(x):
    return (x > 0) - (x < 0)


def naive_arg_cmp(p, q):
    """原点から見て同じ向きなら 0、そうでなければ atan2 で求めた [0, 2π) の偏角で比べる"""
    (px, py), (qx, qy) = p, q
    if px * qy - py * qx == 0 and px * qx + py * qy > 0:
        return 0
    a = math.atan2(py, px) % (2 * math.pi)
    b = math.atan2(qy, qx) % (2 * math.pi)
    return -1 if a < b else 1


def test_docstring_example():
    P = [(-1, -1), (1, 0), (0, 1), (-1, 0), (2, 2), (1, 1), (1, -1)]
    assert cmp_sort(P, arg_cmp) == [(1, 0), (2, 2), (1, 1), (0, 1), (-1, 0), (-1, -1), (1, -1)]


# x 軸の正の向き (偏角 0) から反時計回りに 1 周する順
AROUND = [(1, 0), (2, 1), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (2, -1)]


@pytest.mark.parametrize("i", range(len(AROUND)))
def test_around(i):
    for j in range(len(AROUND)):
        assert sign(arg_cmp(AROUND[i], AROUND[j])) == sign(i - j), (AROUND[i], AROUND[j])


@pytest.mark.parametrize(
    ("p", "q"),
    [
        ((1, 0), (5, 0)),
        ((-1, 0), (-3, 0)),
        ((0, -2), (0, -1)),
        ((2, 3), (4, 6)),
        ((-3, -1), (-6, -2)),
    ],
)
def test_same_direction(p, q):
    assert arg_cmp(p, q) == 0
    assert arg_cmp(q, p) == 0


def test_large_coordinates():
    # atan2 では同じ値になって区別できないほど近い偏角も、正しく比べられる
    p, q = (10**18, 1), (10**18 - 1, 1)
    assert math.atan2(p[1], p[0]) == math.atan2(q[1], q[0])
    assert arg_cmp(p, q) < 0
    assert arg_cmp(q, p) > 0


def test_all_pairs():
    # |x|, |y| <= 6 の原点以外の点のすべての組で、atan2 を使った愚直な比較と一致する
    pts = [(x, y) for x in range(-6, 7) for y in range(-6, 7) if (x, y) != (0, 0)]
    for p in pts:
        for q in pts:
            assert sign(arg_cmp(p, q)) == naive_arg_cmp(p, q), (p, q)


@pytest.mark.parametrize("seed", range(3))
def test_sort_random(seed):
    rng = random.Random(seed)
    pts = [(rng.randint(-10, 10), rng.randint(-10, 10)) for _ in range(500)]
    pts = [p for p in pts if p != (0, 0)]
    assert cmp_sort(pts, arg_cmp) == sorted(pts, key=cmp_to_key(naive_arg_cmp))
