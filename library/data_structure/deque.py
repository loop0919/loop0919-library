# ref: https://github.com/loop0919/loop0919-library/blob/main/library/data_structure/deque.py
from collections.abc import Iterable, Iterator
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class Deque(Generic[T]):
    """\
    ランダムアクセスができる両端キュー
    両端への追加・削除がならし O(1), 添字アクセスが O(1)

    collections.deque は中ほどの添字アクセスが O(N) かかる (PyPy では特に遅い) ので、その代わりに使う
    容量が 2 べきのリングバッファで持ち、満杯になったら容量を 2 倍にする

    Usage::

        dq = Deque([1, 2, 3])
        dq.append(4)
        dq.appendleft(0)
        print(dq)
        # => Deque([0, 1, 2, 3, 4])

        print(dq[2], dq[-1])
        # => 2 4

        print(dq.pop(), dq.popleft())
        # => 4 0

        dq[1] = 10
        print(list(dq), len(dq))
        # => [1, 10, 3] 3
    """

    # 空きを None で埋めるので、要素の型は Any にしておく
    _buf: list[Any]
    _head: int
    _size: int
    _mask: int

    def __init__(self, A: Iterable[T] | None = None):
        """\
        A の要素を先頭から順に並べた両端キューを作る
        Parameters:
            A (Iterable[T] | None): 初期要素 (A 自体は変更しない)。None なら空にする
        """
        # デフォルトを () にすると、Deque() の要素型が Never と推論されて append できなくなる
        buf = [] if A is None else list(A)
        n = len(buf)
        # 容量は n より大きい最小の 2 べき
        cap = 1 << n.bit_length()
        self._buf = buf + [None] * (cap - n)
        self._head = 0
        self._size = n
        self._mask = cap - 1

    def _grow(self) -> None:
        """\
        容量を 2 倍にする (満杯のときだけ呼ぶ)
        先頭の要素が buf[0] に来るように並べ直す
        """
        buf, head = self._buf, self._head
        self._buf = buf[head:] + buf[:head] + [None] * len(buf)
        self._head = 0
        self._mask = 2 * len(buf) - 1

    def append(self, x: T) -> None:
        """\
        末尾に x を追加する
        Parameters:
            x (T): 追加する要素
        """
        if self._size > self._mask:
            self._grow()
        self._buf[(self._head + self._size) & self._mask] = x
        self._size += 1

    def appendleft(self, x: T) -> None:
        """\
        先頭に x を追加する
        Parameters:
            x (T): 追加する要素
        """
        if self._size > self._mask:
            self._grow()
        self._head = (self._head - 1) & self._mask
        self._buf[self._head] = x
        self._size += 1

    def pop(self) -> T:
        """\
        末尾の要素を取り除いて返す
        Returns:
            x (T): 取り除いた末尾の要素
        Raises:
            IndexError: 空のとき
        """
        if self._size == 0:
            raise IndexError("pop from an empty deque")
        self._size -= 1
        return self._buf[(self._head + self._size) & self._mask]

    def popleft(self) -> T:
        """\
        先頭の要素を取り除いて返す
        Returns:
            x (T): 取り除いた先頭の要素
        Raises:
            IndexError: 空のとき
        """
        if self._size == 0:
            raise IndexError("pop from an empty deque")
        x = self._buf[self._head]
        self._head = (self._head + 1) & self._mask
        self._size -= 1
        return x

    def _pos(self, i: int) -> int:
        """\
        先頭から i 番目 (負なら末尾から数える) の要素がある buf 上の位置を返す
        """
        if i < 0:
            i += self._size
        if not 0 <= i < self._size:
            raise IndexError("deque index out of range")
        return (self._head + i) & self._mask

    def __getitem__(self, i: int) -> T:
        return self._buf[self._pos(i)]

    def __setitem__(self, i: int, x: T) -> None:
        self._buf[self._pos(i)] = x

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[T]:
        # 呼んだ時点の要素を写してから走査する (走査中に追加・削除しても壊れない)
        buf, head, end = self._buf, self._head, self._head + self._size
        if end <= len(buf):
            return iter(buf[head:end])
        return iter(buf[head:] + buf[: end - len(buf)])

    def __repr__(self) -> str:
        return f"Deque({list(self)})"
