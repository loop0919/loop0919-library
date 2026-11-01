# ref: https://github.com/loop0919/loop0919-library/blob/main/library/geometry/arg_cmp.py


def arg_cmp(p: tuple[int, int], q: tuple[int, int]) -> int:
    """\
    偏角ソート用の比較関数
    原点から見た点 p, q の偏角を比べる。偏角は x 軸の正の向きを 0 とし、反時計回りに [0, 2π) で測る
    整数だけで計算するので誤差が出ない (math.atan2 で偏角を求めて比べると、近い偏角を区別できないことがある)
    O(1)

    Usage::

        from library.misc.cmp_sort import cmp_sort

        P = [(-1, -1), (1, 0), (0, 1), (-1, 0), (2, 2), (1, 1), (1, -1)]
        print(cmp_sort(P, arg_cmp))
        # => [(1, 0), (2, 2), (1, 1), (0, 1), (-1, 0), (-1, -1), (1, -1)]

    Parameters:
        p, q (tuple[int, int]): 比べる点 (x, y)。原点 (0, 0) は偏角が決まらないので渡さない
    Returns:
        res (int): 偏角が p < q なら負, p == q なら 0, p > q なら正 (cmp_to_key, cmp_sort にそのまま渡せる)
                   原点から見て同じ向きにある点どうしは 0 になる (安定ソートなら元の順序のまま並ぶ)
    """
    px, py = p
    qx, qy = q

    # 偏角が [π, 2π) にあるか (x 軸の負の部分は偏角 π なのでこちらに入れる)
    p_over_180 = py < 0 or (py == 0 and px < 0)
    q_over_180 = qy < 0 or (qy == 0 and qx < 0)

    if p_over_180 != q_over_180:
        # 偏角が [0, π) にある方が前
        return int(p_over_180) - int(q_over_180)
    else:
        # 同じ側にあれば偏角の差は π 未満なので、外積の符号で比べられる
        # 外積 px * qy - py * qx が正なら q は p から見て反時計回り側 (p が前) なので、符号を反転して返す
        return py * qx - px * qy
