import random
from functools import cmp_to_key

import pytest

from library.misc.cmp_sort import _merge_sort, cmp_sort

# CPython では cmp_sort は sorted に任せるので、マージソートも直接テストする
SORTS = [cmp_sort, _merge_sort]


def frac_cmp(a, b):
    """分数 a[0] / a[1] どうしを比べる (分母は正)"""
    return a[0] * b[1] - b[0] * a[1]


def concat_cmp(a, b):
    """連結したときに辞書順で小さくなる方を前にする"""
    return (a + b > b + a) - (a + b < b + a)


def first_cmp(a, b):
    """タプルの先頭だけで比べる (2 番目の値で安定性を確かめる)"""
    return a[0] - b[0]


def expected(A, cmp, reverse=False):
    return sorted(A, key=cmp_to_key(cmp), reverse=reverse)


@pytest.mark.parametrize("sort", SORTS)
def test_docstring_example(sort):
    assert sort([(1, 2), (1, 3), (2, 3), (2, 4)], frac_cmp) == [(1, 3), (1, 2), (2, 4), (2, 3)]
    assert "".join(sort(["3", "30", "34", "5", "9"], concat_cmp)) == "3033459"


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("A", [[], [5], [2, 1], [1, 2], [1, 1]])
def test_small(sort, A):
    assert sort(A, lambda a, b: a - b) == sorted(A)
    assert sort(A, lambda a, b: a - b, reverse=True) == sorted(A, reverse=True)


@pytest.mark.parametrize("sort", SORTS)
def test_stable(sort):
    A = [(1, "a"), (0, "b"), (1, "c"), (0, "d"), (1, "e")]
    assert sort(A, first_cmp) == [(0, "b"), (0, "d"), (1, "a"), (1, "c"), (1, "e")]
    assert sort(A, first_cmp, reverse=True) == [(1, "a"), (1, "c"), (1, "e"), (0, "b"), (0, "d")]


@pytest.mark.parametrize("sort", SORTS)
def test_does_not_modify_input(sort):
    A = [3, 1, 2]
    assert sort(A, lambda a, b: a - b) == [1, 2, 3]
    assert A == [3, 1, 2]


@pytest.mark.parametrize("sort", SORTS)
def test_iterable(sort):
    assert sort((3, 1, 2), lambda a, b: a - b) == [1, 2, 3]
    assert sort((x for x in [3, 1, 2]), lambda a, b: a - b) == [1, 2, 3]


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("reverse", [False, True])
def test_all_lengths(sort, reverse):
    # 2 べきの前後で、末尾に相方のいないブロックができる場合を含めて調べる
    rng = random.Random(0)
    for n in range(70):
        A = [(rng.randint(0, 5), i) for i in range(n)]
        assert sort(A, first_cmp, reverse) == expected(A, first_cmp, reverse), n


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("reverse", [False, True])
def test_sorted_and_reversed_input(sort, reverse):
    A = [(i // 3, i) for i in range(1000)]
    assert sort(A, first_cmp, reverse) == expected(A, first_cmp, reverse)
    A.reverse()
    assert sort(A, first_cmp, reverse) == expected(A, first_cmp, reverse)


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("seed", range(10))
def test_random_fraction(sort, seed):
    rng = random.Random(seed)
    n = rng.randint(1, 3000)
    # 分母と分子を小さくして、値の等しい分数を多くする
    A = [(rng.randint(-10, 10), rng.randint(1, 10)) for _ in range(n)]
    reverse = seed % 2 == 1
    assert sort(A, frac_cmp, reverse) == expected(A, frac_cmp, reverse)


@pytest.mark.parametrize("sort", SORTS)
@pytest.mark.parametrize("seed", range(5))
def test_random_concat(sort, seed):
    rng = random.Random(seed)
    A = [str(rng.randint(1, 1000)) for _ in range(rng.randint(1, 3000))]
    assert sort(A, concat_cmp) == expected(A, concat_cmp)
