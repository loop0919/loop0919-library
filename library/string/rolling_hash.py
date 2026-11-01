# ref: https://github.com/loop0919/loop0919-library/blob/main/library/string/rolling_hash.py

MASK30 = (1 << 30) - 1
MASK31 = (1 << 31) - 1
MASK61 = (1 << 61) - 1


class RollingHash:
    """\
    ローリングハッシュ
    O(N) の前計算のあと、O(1) で文字列区間の一致判定を行うことができる

    Usage::

        rh = RollingHash("ababcccba", 65537)

        print(rh.prod(0, 2) == rh.prod(2, 4))
        # => True

        print(rh.prod(0, 3) == rh.prod(1, 4))
        # => False
    """

    _n: int
    _table: list[int]
    _power: list[int]

    def __init__(self, S: str | list[int], base: int):
        """\
        法 2**61 - 1, 基数base でローリングハッシュを作成する
        base はランダム値を使うと、敵対的なケースにも強くなる
        """
        seq = [ord(c) for c in S] if isinstance(S, str) else S
        n = len(seq)
        mul = self._mul

        # table[i]: S[0:i] のハッシュ値, power[i]: base**i
        table = [0] * (n + 1)
        power = [1] * (n + 1)
        for i, v in enumerate(seq):
            table[i + 1] = (mul(table[i], base) + v) % MASK61
            power[i + 1] = mul(power[i], base)

        self._n = n
        self._table = table
        self._power = power

    @staticmethod
    def _mul(x: int, y: int) -> int:
        """\
        x * y mod 2**61 - 1 を求める
        途中の値が 2**63 未満に収まるように分けて掛ける (PyPy で多倍長整数にならないようにするため)
        """
        x_low, x_high = x & MASK31, x >> 31
        y_low, y_high = y & MASK31, y >> 31
        mid = x_high * y_low + x_low * y_high
        mid_low, mid_high = mid & MASK30, mid >> 30

        ans = (x_high * y_high * 2) + ((mid_low << 31) + mid_high) + (x_low * y_low)
        return ans % MASK61

    def prod(self, l: int, r: int) -> int:
        """\
        区間 [l, r) のハッシュ値を求める (l == r なら空文字列のハッシュ値 0)
        Parameters:
            l (int): 区間の左端
            r (int): 区間の右端 (r 自身は含まない)
        Returns:
            hash (int): S[l:r] のハッシュ値
        """
        assert 0 <= l <= r <= self._n
        return (self._table[r] - self._mul(self._table[l], self._power[r - l])) % MASK61
