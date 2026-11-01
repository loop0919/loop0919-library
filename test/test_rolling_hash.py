import random

import pytest

from library.string.rolling_hash import RollingHash

BASE = 65537


def test_docstring_example():
    rh = RollingHash("ababcccba", BASE)
    assert rh.prod(0, 2) == rh.prod(2, 4)
    assert rh.prod(0, 3) != rh.prod(1, 4)


def test_int_list():
    rh = RollingHash([1, 2, 1, 2, 3], BASE)
    assert rh.prod(0, 2) == rh.prod(2, 4)
    assert rh.prod(1, 3) != rh.prod(2, 4)


def test_compare_between_two_strings():
    # 同じ基数なら、別の文字列から作ったハッシュ同士も比べられる
    s, t = "xxabcxabc", "abc"
    rh_s, rh_t = RollingHash(s, BASE), RollingHash(t, BASE)
    found = [i for i in range(len(s) - len(t) + 1) if rh_s.prod(i, i + len(t)) == rh_t.prod(0, len(t))]
    assert found == [2, 6]


def test_empty_range():
    # 長さ 0 の区間は、位置や元の文字列によらず同じハッシュ値になる
    rh_s, rh_t = RollingHash("abcde", BASE), RollingHash("", BASE)
    assert rh_s.prod(0, 0) == rh_s.prod(3, 3) == rh_s.prod(5, 5) == rh_t.prod(0, 0)


@pytest.mark.parametrize(("l", "r"), [(-1, 2), (2, 1), (0, 6), (6, 6)])
def test_invalid_range(l, r):
    rh = RollingHash("abcde", BASE)
    with pytest.raises(AssertionError):
        rh.prod(l, r)


@pytest.mark.parametrize("seed", range(20))
def test_random_string(seed):
    # 部分文字列が等しいこととハッシュが等しいことが一致するか、すべての区間で確かめる
    rng = random.Random(seed)
    s = "".join(rng.choice("ab") for _ in range(rng.randint(1, 40)))
    base = rng.randrange(2, (1 << 61) - 1)
    rh = RollingHash(s, base)

    hash_of: dict[str, int] = {}
    for l in range(len(s) + 1):
        for r in range(l, len(s) + 1):
            h = rh.prod(l, r)
            assert 0 <= h < (1 << 61) - 1
            assert hash_of.setdefault(s[l:r], h) == h
    assert len(set(hash_of.values())) == len(hash_of)
