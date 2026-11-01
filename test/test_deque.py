import random
from collections import deque

import pytest

from library.data_structure.deque import Deque


def test_docstring_example():
    dq = Deque([1, 2, 3])
    dq.append(4)
    dq.appendleft(0)
    assert list(dq) == [0, 1, 2, 3, 4]
    assert dq[2] == 2
    assert dq[-1] == 4
    assert dq.pop() == 4
    assert dq.popleft() == 0
    dq[1] = 10
    assert list(dq) == [1, 10, 3]
    assert len(dq) == 3


def test_init():
    assert list(Deque()) == []
    assert list(Deque([5, 6, 7])) == [5, 6, 7]
    assert list(Deque(x * x for x in range(4))) == [0, 1, 4, 9]


def test_init_does_not_modify_input():
    A = [1, 2, 3]
    dq = Deque(A)
    dq.append(4)
    dq[0] = 100
    assert A == [1, 2, 3]


def test_len_and_bool():
    dq = Deque()
    assert len(dq) == 0
    assert not dq
    dq.append(1)
    assert len(dq) == 1
    assert dq
    dq.pop()
    assert not dq


def test_append_and_appendleft_order():
    dq = Deque()
    dq.append(1)
    dq.appendleft(2)
    dq.append(3)
    dq.appendleft(4)
    assert list(dq) == [4, 2, 1, 3]


def test_pop_and_popleft():
    dq = Deque([1, 2, 3, 4])
    assert dq.pop() == 4
    assert dq.popleft() == 1
    assert dq.pop() == 3
    assert dq.popleft() == 2
    assert len(dq) == 0


@pytest.mark.parametrize("method", ["pop", "popleft"])
def test_pop_from_empty_raises(method):
    dq = Deque([1])
    dq.pop()
    with pytest.raises(IndexError):
        getattr(dq, method)()


def test_getitem():
    dq = Deque([10, 20, 30])
    assert [dq[0], dq[1], dq[2]] == [10, 20, 30]
    assert [dq[-1], dq[-2], dq[-3]] == [30, 20, 10]


def test_setitem():
    dq = Deque([10, 20, 30])
    dq[0] = 1
    dq[-1] = 3
    assert list(dq) == [1, 20, 3]


@pytest.mark.parametrize("i", [3, 4, -4, -5])
def test_index_out_of_range_raises(i):
    dq = Deque([10, 20, 30])
    with pytest.raises(IndexError):
        dq[i]
    with pytest.raises(IndexError):
        dq[i] = 0


def test_index_out_of_range_after_pop():
    # 取り出した位置にはもうアクセスできない
    dq = Deque([10, 20, 30])
    dq.pop()
    dq.popleft()
    assert dq[0] == 20
    with pytest.raises(IndexError):
        dq[1]
    with pytest.raises(IndexError):
        dq[-2]


def test_repr():
    assert repr(Deque([1, 2, 3])) == "Deque([1, 2, 3])"
    assert repr(Deque()) == "Deque([])"


def test_grow_while_wrapped():
    # 左右から交互に積んで、先頭がバッファの途中にある状態で容量を何度も増やす
    dq = Deque()
    for i in range(100):
        dq.appendleft(-i)
        dq.append(i)
    assert list(dq) == list(range(-99, 1)) + list(range(100))
    assert dq[0] == -99
    assert dq[99] == 0
    assert dq[100] == 0
    assert dq[-1] == 99


def test_grow_after_rotation():
    # 先頭を末尾に回し続けて先頭位置をずらしてから、容量を増やす
    dq = Deque(range(5))
    for _ in range(3):
        dq.append(dq.popleft())
    for i in range(5, 20):
        dq.append(i)
    assert list(dq) == [3, 4, 0, 1, 2, *range(5, 20)]


def test_iter_is_snapshot():
    # 走査中に追加しても、走査を始めた時点の要素だけを返す
    dq = Deque([1, 2, 3])
    seen = []
    for x in dq:
        seen.append(x)
        dq.append(x)
    assert seen == [1, 2, 3]
    assert list(dq) == [1, 2, 3, 1, 2, 3]


@pytest.mark.parametrize("seed", range(20))
def test_random_operations(seed):
    # collections.deque と同じ操作をして、結果と中身を比べる
    rng = random.Random(seed)
    dq = Deque()
    ref = deque()
    for _ in range(2000):
        op = rng.randrange(6)
        if op == 0:
            x = rng.randrange(10**9)
            dq.append(x)
            ref.append(x)
        elif op == 1:
            x = rng.randrange(10**9)
            dq.appendleft(x)
            ref.appendleft(x)
        elif op == 2 and ref:
            assert dq.pop() == ref.pop()
        elif op == 3 and ref:
            assert dq.popleft() == ref.popleft()
        elif op == 4 and ref:
            i = rng.randrange(-len(ref), len(ref))
            assert dq[i] == ref[i]
        elif op == 5 and ref:
            i = rng.randrange(-len(ref), len(ref))
            x = rng.randrange(10**9)
            dq[i] = x
            ref[i] = x
        assert len(dq) == len(ref)
    assert list(dq) == list(ref)
