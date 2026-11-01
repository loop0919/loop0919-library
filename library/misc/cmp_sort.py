# ref: https://github.com/loop0919/loop0919-library/blob/main/library/misc/cmp_sort.py
import sys
from collections.abc import Callable, Iterable
from functools import cmp_to_key
from typing import TypeVar

T = TypeVar("T")


def cmp_sort(A: Iterable[T], cmp: Callable[[T, T], int], reverse: bool = False) -> list[T]:
    """\
    比較関数 cmp で A を安定ソートした新しいリストを返す
    sorted(A, key=cmp_to_key(cmp), reverse=reverse) と同じ結果になる
    比較 O(N log N) 回

    PyPy では cmp_to_key が遅いので、自前のマージソートを使う (N = 2 * 10**5 で 10 倍ほど速い)
    CPython では C で書かれた sorted の方が速いので、cmp_to_key をそのまま使う

    Usage::

        # 分数 a[0] / a[1] の昇順 (分母は正)
        A = [(1, 2), (1, 3), (2, 3), (2, 4)]
        print(cmp_sort(A, lambda a, b: a[0] * b[1] - b[0] * a[1]))
        # => [(1, 3), (1, 2), (2, 4), (2, 3)]

        # 連結したときに辞書順最小になる並べ方
        S = ["3", "30", "34", "5", "9"]
        print("".join(cmp_sort(S, lambda a, b: (a + b > b + a) - (a + b < b + a))))
        # => 3033459

    Parameters:
        A (Iterable[T]): ソートする列 (A 自体は変更しない)
        cmp (Callable[[T, T], int]): a < b なら負, a == b なら 0, a > b なら正を返す関数 (cmp_to_key と同じ)
        reverse (bool): True なら降順にする (等しい要素の順序は保つ)
    Returns:
        sorted (list[T]): ソートした新しいリスト
    """
    if sys.implementation.name != "pypy":
        return sorted(A, key=cmp_to_key(cmp), reverse=reverse)
    return _merge_sort(A, cmp, reverse)


def _merge_sort(A: Iterable[T], cmp: Callable[[T, T], int], reverse: bool = False) -> list[T]:
    """\
    ボトムアップのマージソートで、cmp_sort と同じ結果を返す
    長さ width の整列済みブロックを隣どうし併合して、width を倍々にしていく
    """
    src = list(A)
    n = len(src)

    # 逆順にしてから昇順に安定ソートして戻すと、等しい要素の順序を保ったまま降順になる
    if reverse:
        src.reverse()

    dst = src[:]
    width = 1
    while width < n:
        for lo in range(0, n, 2 * width):
            mid = lo + width
            # 相方のいない末尾のブロックはそのまま写す
            if mid >= n:
                dst[lo:] = src[lo:]
                break
            hi = min(mid + width, n)

            # src[lo:mid] と src[mid:hi] を dst[lo:hi] に併合する
            # 右が真に小さいときだけ右から取るので、安定ソートになる
            i, j, k = lo, mid, lo
            x, y = src[i], src[j]
            while True:
                if cmp(y, x) < 0:
                    dst[k] = y
                    k += 1
                    j += 1
                    if j == hi:
                        dst[k:hi] = src[i:mid]
                        break
                    y = src[j]
                else:
                    dst[k] = x
                    k += 1
                    i += 1
                    if i == mid:
                        dst[k:hi] = src[j:hi]
                        break
                    x = src[i]
        src, dst = dst, src
        width *= 2

    if reverse:
        src.reverse()
    return src
