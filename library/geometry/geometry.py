# ref: https://github.com/loop0919/loop0919-library/blob/main/library/geometry/geometry.py
"""\
幾何ライブラリ
点は複素数 complex で表す (実部が x 座標, 虚部が y 座標)

参考: https://ei1333.github.io/luzhiled/snippets/geometry/template.html
intersect, distance, crosspoint, tangent は、引数の図形の型を見て処理を振り分ける (C++ の多重定義の代わり)
振り分け先の関数は、名前の後ろに図形の種類を付けたもの (例: intersect_segment_segment, distance_line_point)
提出コードを短くしたいときや、型を見る手間を省きたいときはこちらを直接呼ぶ

返り値の型は、引数の図形の組によらずそろえてある
    intersect 系: 共有点の個数 (int)。無限にあるなら INF (= 1 << 60)
    crosspoint 系: (交点のリスト, 共有点が無限にあるか)。無限にあるなら ([], True)
    tangent 系: 接線 (Line) のリスト。各直線の a は円との接点

誤差は EPS まで許す。座標の絶対値がとても大きい・小さいときは EPS を調整する
Line, Segment の 2 点 a, b は異なるものとし、Circle の半径は正とする
多角形は頂点を反時計回りに並べたリストで表す

Usage::

    s = Segment(0 + 0j, 2 + 2j)
    t = Segment(0 + 2j, 2 + 0j)
    print(intersect(s, t), crosspoint(s, t), distance(s, 3 + 3j))
    # => 1 ([(1+1j)], False) 1.4142135623730951

    print(intersect(s, Segment(1 + 1j, 3 + 3j)), crosspoint(s, Segment(1 + 1j, 3 + 3j)))
    # => 1152921504606846976 ([], True)

    poly = convex_hull([0j, 2 + 0j, 1 + 1j, 2 + 2j, 0 + 2j])
    print(poly, area(poly))
    # => [0j, (2+0j), (2+2j), 2j] 4.0

    c = Circle(0j, 1.0)
    print(crosspoint(c, Line(-2 + 0j, 2 + 0j)))
    # => ([(-1+0j), (1+0j)], False)
"""

import math
from collections.abc import Iterable, Sequence
from itertools import pairwise

EPS = 1e-8

# ccw(a, b, c) の返り値
COUNTER_CLOCKWISE = 1  # a -> b -> c が反時計回り
CLOCKWISE = -1  # a -> b -> c が時計回り
ONLINE_BACK = 2  # c, a, b の順に一直線上
ONLINE_FRONT = -2  # a, b, c の順に一直線上
ON_SEGMENT = 0  # c が線分 ab 上 (端点を含む)

# contains(poly, p) の返り値
OUT = 0
ON = 1
IN = 2

# intersect 系の関数で、共有点が無限にあるときの返り値
INF = 1 << 60


class Line:
    """\
    2 点 a, b を通る直線 (a != b)
    a から b への向きを持つ (convex_cut などで使う)
    """

    __slots__ = ("a", "b")

    a: complex
    b: complex

    def __init__(self, a: complex, b: complex):
        self.a = a
        self.b = b

    @classmethod
    def from_equation(cls, A: float, B: float, C: float) -> "Line":
        """\
        直線 Ax + By = C を作る
        Parameters:
            A, B, C (float): 直線の式の係数 ((A, B) != (0, 0))
        Returns:
            line (Line): 直線 Ax + By = C
        """
        n = complex(A, B)
        # 原点から直線に下ろした垂線の足と、そこから法線 n を 90 度回した向きに進んだ点
        a = n * (C / norm(n))
        return cls(a, a + n * 1j)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.a!r}, {self.b!r})"


class Segment(Line):
    """\
    2 点 a, b を端点とする線分 (a != b)
    Line を継承しているので、直線を受け取る関数に渡すと a, b を通る直線として扱う
    """

    __slots__ = ()


class Circle:
    """\
    中心 p, 半径 r の円 (r > 0)
    """

    __slots__ = ("p", "r")

    p: complex
    r: float

    def __init__(self, p: complex, r: float):
        self.p = p
        self.r = r

    def __repr__(self) -> str:
        return f"Circle({self.p!r}, {self.r!r})"


def eq(a: float, b: float) -> bool:
    """\
    a, b の差が EPS 未満なら等しいとみなす
    """
    return abs(a - b) < EPS


def _sign(x: float) -> int:
    """\
    x の符号を誤差 EPS 込みで -1, 0, 1 で返す
    """
    return 1 if x > EPS else -1 if x < -EPS else 0


def _point_key(p: complex) -> tuple[float, float]:
    """\
    点を (x, y) の辞書順で並べるためのキー
    """
    return (p.real, p.imag)


def cross(a: complex, b: complex) -> float:
    """\
    外積 a.x * b.y - a.y * b.x を返す
    正なら b は a から見て反時計回り側、負なら時計回り側にある
    """
    return a.real * b.imag - a.imag * b.real


def dot(a: complex, b: complex) -> float:
    """\
    内積 a.x * b.x + a.y * b.y を返す
    """
    return a.real * b.real + a.imag * b.imag


def norm(a: complex) -> float:
    """\
    絶対値の 2 乗 |a|^2 を返す
    """
    return a.real * a.real + a.imag * a.imag


def rotate(theta: float, p: complex) -> complex:
    """\
    点 p を原点中心に反時計回りに theta 回転した点を返す
    Parameters:
        theta (float): 回転角 (ラジアン)
        p (complex): 回転する点
    Returns:
        q (complex): 回転後の点
    """
    return p * complex(math.cos(theta), math.sin(theta))


def get_angle(a: complex, b: complex, c: complex) -> float:
    """\
    点 b での角 abc の大きさを [0, π] のラジアンで返す
    度数法にするときは math.degrees を使う
    """
    v, w = a - b, c - b
    return math.atan2(abs(cross(v, w)), dot(v, w))


def get_signed_angle(a: complex, b: complex, c: complex) -> float:
    """\
    点 b を中心に、半直線 ba を半直線 bc に重ねる回転角を (-π, π] のラジアンで返す
    反時計回りが正なので、rotate(get_signed_angle(a, b, c), a - b) は c - b と同じ向きになる
    abs を取ると get_angle(a, b, c) と同じになる
    """
    v, w = a - b, c - b
    theta = math.atan2(cross(v, w), dot(v, w))
    # cross が -0.0 だと atan2 は -π を返すので、π にそろえる
    return math.pi if theta == -math.pi else theta


def ccw(a: complex, b: complex, c: complex) -> int:
    """\
    a から見た b, c の位置関係を返す
    Returns:
        COUNTER_CLOCKWISE (1): a -> b -> c が反時計回り
        CLOCKWISE (-1): a -> b -> c が時計回り
        ONLINE_BACK (2): c, a, b の順に一直線上
        ONLINE_FRONT (-2): a, b, c の順に一直線上
        ON_SEGMENT (0): c が線分 ab 上 (端点を含む)
    """
    b, c = b - a, c - a
    cr = cross(b, c)
    if cr > EPS:
        return COUNTER_CLOCKWISE
    if cr < -EPS:
        return CLOCKWISE
    if dot(b, c) < -EPS:
        return ONLINE_BACK
    if norm(b) + EPS < norm(c):
        return ONLINE_FRONT
    return ON_SEGMENT


def parallel(l: Line, m: Line) -> bool:
    """\
    直線 l, m が平行か (同じ直線も平行とみなす)
    """
    return eq(cross(l.b - l.a, m.b - m.a), 0.0)


def orthogonal(l: Line, m: Line) -> bool:
    """\
    直線 l, m が垂直か
    """
    return eq(dot(l.b - l.a, m.b - m.a), 0.0)


def get_signed_angle_line_line(l: Line, m: Line) -> float:
    """\
    直線 l の向き (l.a -> l.b) を直線 m の向き (m.a -> m.b) に重ねる回転角を (-π, π] のラジアンで返す
    反時計回りが正。平行なら、同じ向きで 0、逆向きで π をちょうど返す
    向きを区別しない 2 直線のなす角 ([0, π/2]) は、θ = abs(返り値) として min(θ, π - θ) で求まる
    """
    d, e = l.b - l.a, m.b - m.a
    if parallel(l, m):
        return 0.0 if dot(d, e) > 0 else math.pi
    return math.atan2(cross(d, e), dot(d, e))


def projection(l: Line, p: complex) -> complex:
    """\
    点 p から直線 l に下ろした垂線の足を返す
    """
    d = l.b - l.a
    return l.a + d * (dot(p - l.a, d) / norm(d))


def reflection(l: Line, p: complex) -> complex:
    """\
    直線 l を対称軸として点 p と線対称な点を返す
    """
    return 2 * projection(l, p) - p


def intersect_line_point(l: Line, p: complex) -> int:
    """\
    直線 l と点 p の共有点の個数 (p が l 上なら 1, そうでなければ 0) を返す
    """
    return int(abs(ccw(l.a, l.b, p)) != 1)


def intersect_segment_point(s: Segment, p: complex) -> int:
    """\
    線分 s と点 p の共有点の個数 (p が s 上 (端点を含む) なら 1, そうでなければ 0) を返す
    """
    return int(ccw(s.a, s.b, p) == ON_SEGMENT)


def intersect_circle_point(c: Circle, p: complex) -> int:
    """\
    円 c の周と点 p の共有点の個数 (p が周上なら 1, そうでなければ 0) を返す
    """
    return int(eq(abs(p - c.p), c.r))


def intersect_line_line(l: Line, m: Line) -> int:
    """\
    直線 l, m の共有点の個数を返す
    Returns:
        count (int): 交わるなら 1, 平行なら 0, 同じ直線なら INF
    """
    if not parallel(l, m):
        return 1
    return INF if intersect_line_point(l, m.a) else 0


def intersect_line_segment(l: Line, s: Segment) -> int:
    """\
    直線 l と線分 s の共有点の個数を返す
    Returns:
        count (int): 交わる (端点が l 上にある場合を含む) なら 1, 交わらないなら 0, s が l 上にあるなら INF
    """
    d = l.b - l.a
    sa, sb = _sign(cross(d, s.a - l.a)), _sign(cross(d, s.b - l.a))
    if sa == sb == 0:
        return INF
    return int(sa * sb <= 0)


def intersect_segment_segment(s: Segment, t: Segment) -> int:
    """\
    線分 s, t の共有点の個数を返す
    Returns:
        count (int): 1 点で交わる (端点で接する場合を含む) なら 1, 交わらないなら 0,
                     同じ直線上で重なる部分が長さを持つなら INF
    """
    if ccw(s.a, s.b, t.a) * ccw(s.a, s.b, t.b) > 0 or ccw(t.a, t.b, s.a) * ccw(t.a, t.b, s.b) > 0:
        return 0
    if not parallel(s, t):
        return 1
    # 同じ直線上にあるので、s の向きに沿った位置で重なる部分の長さを求める
    d = s.b - s.a
    length = abs(d)
    ta, tb = dot(t.a - s.a, d) / length, dot(t.b - s.a, d) / length
    overlap = min(length, max(ta, tb)) - max(0.0, min(ta, tb))
    return INF if overlap > EPS else 1


def intersect_circle_line(c: Circle, l: Line) -> int:
    """\
    円 c の周と直線 l の共有点の個数 (0, 1, 2) を返す (接するなら 1)
    """
    return len(crosspoint_circle_line(c, l)[0])


def intersect_circle_segment(c: Circle, s: Segment) -> int:
    """\
    円 c の周と線分 s の共有点の個数 (0, 1, 2) を返す
    接する場合は 1 個と数える。線分が円の内部に収まるときは 0 個
    """
    return len(crosspoint_circle_segment(c, s)[0])


def count_common_tangents(c1: Circle, c2: Circle) -> int:
    """\
    円 c1, c2 の共通接線の本数を返す (2 円の位置関係の判定に使う)
    Returns:
        4: 離れている
        3: 外接する
        2: 2 点で交わる
        1: 内接する
        0: 一方が他方を含む
        INF: 一致する
    """
    if c1.r < c2.r:
        c1, c2 = c2, c1
    d = abs(c1.p - c2.p)
    if c1.r + c2.r < d - EPS:
        return 4
    if eq(c1.r + c2.r, d):
        return 3
    if c1.r - c2.r < d - EPS:
        return 2
    if eq(c1.r - c2.r, d):
        return INF if d < EPS else 1
    return 0


def intersect_circle_circle(c1: Circle, c2: Circle) -> int:
    """\
    円 c1, c2 の周の共有点の個数を返す
    Returns:
        count (int): 2 点で交わるなら 2, 接するなら 1, 交わらないなら 0, 一致するなら INF
    """
    k = count_common_tangents(c1, c2)
    if k == INF:
        return INF
    return (0, 1, 2, 1, 0)[k]


def distance_point_point(p: complex, q: complex) -> float:
    """\
    点 p, q の距離を返す
    """
    return abs(p - q)


def distance_line_point(l: Line, p: complex) -> float:
    """\
    直線 l と点 p の距離を返す
    """
    return abs(p - projection(l, p))


def distance_segment_point(s: Segment, p: complex) -> float:
    """\
    線分 s と点 p の距離を返す
    """
    # 垂線の足が線分の外に出るなら、近い方の端点までの距離になる
    if dot(s.b - s.a, p - s.a) < 0:
        return abs(p - s.a)
    if dot(s.a - s.b, p - s.b) < 0:
        return abs(p - s.b)
    return distance_line_point(s, p)


def distance_line_line(l: Line, m: Line) -> float:
    """\
    直線 l, m の距離を返す (交わるなら 0)
    """
    return 0.0 if intersect_line_line(l, m) else distance_line_point(l, m.a)


def distance_line_segment(l: Line, s: Segment) -> float:
    """\
    直線 l と線分 s の距離を返す (交わるなら 0)
    """
    if intersect_line_segment(l, s):
        return 0.0
    return min(distance_line_point(l, s.a), distance_line_point(l, s.b))


def distance_segment_segment(s: Segment, t: Segment) -> float:
    """\
    線分 s, t の距離を返す (交わるなら 0)
    """
    if intersect_segment_segment(s, t):
        return 0.0
    return min(
        distance_segment_point(s, t.a),
        distance_segment_point(s, t.b),
        distance_segment_point(t, s.a),
        distance_segment_point(t, s.b),
    )


# crosspoint 系の関数は (交点のリスト, 共有点が無限にあるか) を返す
# 共有点が無限にあるときは ([], True) になる


def _crosspoint(l: Line, m: Line) -> complex:
    """\
    平行でない直線 l, m の交点を返す
    """
    d = l.b - l.a
    return m.a + (m.b - m.a) * (cross(d, l.b - m.a) / cross(d, m.b - m.a))


def crosspoint_line_line(l: Line, m: Line) -> tuple[list[complex], bool]:
    """\
    直線 l, m の交点を返す
    Returns:
        points (list[complex]): 交点のリスト (交わるなら 1 点, 平行なら空)
        infinite (bool): 同じ直線なら True (points は空)
    """
    k = intersect_line_line(l, m)
    if k == INF:
        return [], True
    if k == 0:
        return [], False
    return [_crosspoint(l, m)], False


def crosspoint_line_segment(l: Line, s: Segment) -> tuple[list[complex], bool]:
    """\
    直線 l と線分 s の交点を返す
    Returns:
        points (list[complex]): 交点のリスト (交わるなら 1 点, 交わらないなら空)
        infinite (bool): s が l 上にあるなら True (points は空)
    """
    k = intersect_line_segment(l, s)
    if k == INF:
        return [], True
    if k == 0:
        return [], False
    return [_crosspoint(l, s)], False


def crosspoint_segment_segment(s: Segment, t: Segment) -> tuple[list[complex], bool]:
    """\
    線分 s, t の交点を返す
    Returns:
        points (list[complex]): 交点のリスト (1 点で交わる・接するなら 1 点, 交わらないなら空)
        infinite (bool): 同じ直線上で重なる部分が長さを持つなら True (points は空)
    """
    k = intersect_segment_segment(s, t)
    if k == INF:
        return [], True
    if k == 0:
        return [], False
    if parallel(s, t):
        # 同じ直線上で、端点どうしが接している
        return [s.a if intersect_segment_point(t, s.a) else s.b], False
    return [_crosspoint(s, t)], False


def crosspoint_circle_line(c: Circle, l: Line) -> tuple[list[complex], bool]:
    """\
    円 c の周と直線 l の交点を返す
    Returns:
        points (list[complex]): 交点のリスト。2 点で交わるなら l.a から l.b の向きに並べた 2 点、
                                接するなら接点 1 点、交わらないなら空
        infinite (bool): 常に False
    """
    h = projection(l, c.p)
    dist = abs(h - c.p)
    if dist > c.r + EPS:
        return [], False
    if eq(dist, c.r):
        return [h], False
    e = (l.b - l.a) / abs(l.b - l.a)
    base = math.sqrt(max(0.0, c.r * c.r - dist * dist))
    return [h - e * base, h + e * base], False


def crosspoint_circle_segment(c: Circle, s: Segment) -> tuple[list[complex], bool]:
    """\
    円 c の周と線分 s の交点を返す
    Returns:
        points (list[complex]): 交点を s.a に近い順に並べたリスト (0 ~ 2 点, 接点は 1 点と数える)
        infinite (bool): 常に False
    """
    d = s.b - s.a
    length = abs(d)
    res = []
    for q in crosspoint_circle_line(c, s)[0]:
        # s.a から q までの、s の向きに沿った長さが [0, |d|] に入れば線分上
        t = dot(q - s.a, d) / length
        if -EPS <= t <= length + EPS:
            res.append(q)
    return res, False


def crosspoint_circle_circle(c1: Circle, c2: Circle) -> tuple[list[complex], bool]:
    """\
    円 c1, c2 の周の交点を返す
    Returns:
        points (list[complex]): 交点のリスト。2 点で交わるなら c1 の中心から c2 の中心へ向かって左側, 右側の順の 2 点、
                                接するなら接点 1 点、交わらないなら空
        infinite (bool): 2 円が一致するなら True (points は空)
    """
    k = count_common_tangents(c1, c2)
    if k == INF:
        return [], True
    if k == 0 or k == 4:
        return [], False
    d = abs(c2.p - c1.p)
    u = (c2.p - c1.p) / d
    # c1 の中心から、交点を結ぶ線分の中点までの長さ
    x = (d * d + c1.r * c1.r - c2.r * c2.r) / (2 * d)
    if k == 1 or k == 3:
        return [c1.p + u * x], False
    y = math.sqrt(max(0.0, c1.r * c1.r - x * x))
    return [c1.p + u * complex(x, y), c1.p + u * complex(x, -y)], False


def tangent_circle_point(c: Circle, p: complex) -> list[Line]:
    """\
    点 p を通る円 c の接線を返す
    Returns:
        lines (list[Line]): 接線のリスト。p が円の外なら 2 本、周上なら 1 本、内部なら空
                            各直線の a は円との接点で、b は p (p が周上のときは接線上の別の点)
    """
    v = p - c.p
    d = abs(v)
    if d < c.r - EPS:
        return []
    if eq(d, c.r):
        return [Line(p, p + v * 1j)]
    # 接点は、中心から p の向きに r^2 / d 進み、そこから垂直に r * sqrt(d^2 - r^2) / d ずれた位置にある
    u = v / d
    x = c.r * c.r / d
    y = c.r * math.sqrt(d * d - c.r * c.r) / d
    return [Line(c.p + u * complex(x, y), p), Line(c.p + u * complex(x, -y), p)]


def tangent_circle_circle(c1: Circle, c2: Circle) -> list[Line]:
    """\
    円 c1, c2 の共通接線を返す
    本数は count_common_tangents(c1, c2) と同じ (2 円が一致するときだけは空)
    Returns:
        lines (list[Line]): 共通接線のリスト。各直線の a は c1 との接点
                            2 円の接点で引いた接線だけは、b が c2 との接点ではない (c2 との接点は a と同じ)
    """
    res: list[Line] = []
    g = norm(c2.p - c1.p)
    if eq(g, 0.0):
        return res
    d = math.sqrt(g)
    u = (c2.p - c1.p) / d
    v = u * 1j
    # s = -1 が共通外接線, s = 1 が共通内接線
    for s in (-1, 1):
        # 接線の単位法線 n は dot(n, u) = h を満たす
        h = (c1.r + s * c2.r) / d
        if eq(1 - h * h, 0.0):
            q = c1.p + u * (c1.r if h > 0 else -c1.r)
            res.append(Line(q, q + v))
        elif 1 - h * h > 0:
            uu, vv = u * h, v * math.sqrt(1 - h * h)
            res.append(Line(c1.p + (uu + vv) * c1.r, c2.p - (uu + vv) * (c2.r * s)))
            res.append(Line(c1.p + (uu - vv) * c1.r, c2.p - (uu - vv) * (c2.r * s)))
    return res


def area(poly: Sequence[complex], c: Circle | None = None) -> float:
    """\
    多角形の符号付き面積を返す (反時計回りなら正, 時計回りなら負)
    c を渡すと、多角形と円 c の共通部分の符号付き面積を返す (area_polygon_circle)
    """
    if c is not None:
        return area_polygon_circle(poly, c)
    return sum(cross(poly[i - 1], poly[i]) for i in range(len(poly))) / 2


def is_convex(poly: Sequence[complex]) -> bool:
    """\
    反時計回りに並べた多角形が凸か (一直線に並ぶ頂点があってもよい)
    """
    n = len(poly)
    return all(ccw(poly[i - 1], poly[i], poly[(i + 1) % n]) != CLOCKWISE for i in range(n))


def contains(poly: Sequence[complex], p: complex) -> int:
    """\
    多角形 poly と点 p の位置関係を返す (poly は凸でなくてもよい, 向きも問わない)
    Returns:
        IN (2): 内部, ON (1): 辺上, OUT (0): 外部
    """
    inside = False
    for i in range(len(poly)):
        a, b = poly[i - 1] - p, poly[i] - p
        if a.imag > b.imag:
            a, b = b, a
        cr = cross(a, b)
        if abs(cr) < EPS and dot(a, b) < EPS:
            return ON
        # p から x 軸の正の向きに伸ばした半直線が、辺 ab と交わる回数の偶奇を数える
        if a.imag <= 0 < b.imag and cr > 0:
            inside = not inside
    return IN if inside else OUT


def convex_hull(ps: Iterable[complex], strict: bool = True) -> list[complex]:
    """\
    点集合の凸包を求める (Andrew's monotone chain)
    O(N log N)
    Parameters:
        ps (Iterable[complex]): 点集合 (重複があってもよい, ps 自体は変更しない)
        strict (bool): True なら凸包の辺上にある点を含めない。False なら含める
    Returns:
        hull (list[complex]): 凸包の頂点を、(x, y) が辞書順最小の点から反時計回りに並べたリスト
                              全点が一直線上にあるときは、strict なら両端の 2 点、そうでなければ全点を端から順に返す
    """
    pts = sorted(set(ps), key=_point_key)
    if len(pts) <= 2:
        return pts
    # 曲がり方がこれ未満なら、最後の点を取り除く
    th = EPS if strict else -EPS

    def half(seq: Iterable[complex]) -> list[complex]:
        ch: list[complex] = []
        for p in seq:
            while len(ch) >= 2 and cross(ch[-1] - ch[-2], p - ch[-1]) < th:
                ch.pop()
            ch.append(p)
        return ch

    lower = half(pts)
    upper = half(reversed(pts))
    # 辺上の点を含めて全点が一直線上にあると、下側と上側のどちらにも全点が入る
    if not strict and len(lower) == len(upper) == len(pts):
        return pts
    return lower[:-1] + upper[:-1]


def convex_cut(poly: Sequence[complex], l: Line) -> list[complex]:
    """\
    凸多角形 poly を直線 l で切り、l.a から l.b を見て左側 (l 上を含む) に残る凸多角形を返す
    """
    n = len(poly)
    d = l.b - l.a
    side = [_sign(cross(d, p - l.a)) for p in poly]
    res = []
    for i in range(n):
        j = (i + 1) % n
        if side[i] >= 0:
            res.append(poly[i])
        if side[i] * side[j] < 0:
            res.append(_crosspoint(Line(poly[i], poly[j]), l))
    return res


def area_polygon_circle(poly: Sequence[complex], c: Circle) -> float:
    """\
    多角形 poly と円 c の共通部分の符号付き面積を返す (poly が反時計回りなら正)
    poly は凸でなくてもよい
    O(N)
    """
    n = len(poly)
    if n < 3:
        return 0.0
    r2 = c.r * c.r
    res = 0.0
    for i in range(n):
        a, b = poly[i - 1], poly[i]
        # 円の中心, a, b の三角形と円の共通部分の符号付き面積 (の 2 倍) を足していく
        if abs(cross(a - c.p, b - c.p)) < EPS:
            continue
        # 辺を円周との交点で区切ると、各区間は円の内側か外側の一方だけを通る
        pts = [a, *crosspoint_circle_segment(c, Segment(a, b))[0], b]
        for u, v in pairwise(pts):
            vu, vv = u - c.p, v - c.p
            if abs((u + v) / 2 - c.p) < c.r:
                res += cross(vu, vv)
            else:
                res += r2 * math.atan2(cross(vu, vv), dot(vu, vv))
    return res / 2


def convex_diameter(poly: Sequence[complex]) -> float:
    """\
    反時計回りに並べた凸多角形の直径 (最も遠い頂点対の距離) を求める (キャリパー法)
    O(N)
    """
    n = len(poly)
    # y 座標が最大の点と最小の点から始めて、2 本の平行な支持線を回していく
    i = max(range(n), key=lambda k: poly[k].imag)
    j = min(range(n), key=lambda k: poly[k].imag)
    best = norm(poly[i] - poly[j])
    for _ in range(2 * n):
        if cross(poly[(i + 1) % n] - poly[i], poly[(j + 1) % n] - poly[j]) >= 0:
            j = (j + 1) % n
        else:
            i = (i + 1) % n
        best = max(best, norm(poly[i] - poly[j]))
    return math.sqrt(best)


def closest_pair(ps: Iterable[complex]) -> float:
    """\
    最近点対の距離を求める (分割統治法)
    O(N log N)
    Parameters:
        ps (Iterable[complex]): 2 点以上の点集合 (ps 自体は変更しない)
    Returns:
        dist (float): 最も近い 2 点の距離 (同じ点が 2 つあれば 0)
    Raises:
        ValueError: 点が 2 つ未満のとき
    """
    pts = sorted(ps, key=_point_key)
    if len(pts) < 2:
        raise ValueError("closest_pair requires at least 2 points")

    def rec(l: int, r: int) -> float:
        """\
        pts[l:r] の最近点対の距離を返し、pts[l:r] を y 座標の昇順に並べ替える
        """
        if r - l <= 1:
            return math.inf
        m = (l + r) // 2
        x = pts[m].real
        d = min(rec(l, m), rec(m, r))
        # 左右とも y 座標でソート済みなので、sorted (TimSort) は線形時間のマージになる
        pts[l:r] = sorted(pts[l:r], key=lambda p: p.imag)
        near: list[complex] = []
        for p in pts[l:r]:
            if abs(p.real - x) >= d:
                continue
            for q in reversed(near):
                if p.imag - q.imag >= d:
                    break
                d = min(d, abs(p - q))
            near.append(p)
        return d

    return rec(0, len(pts))


def merge_segments(segs: Iterable[Segment]) -> list[Segment]:
    """\
    同じ直線上にあって共有点を持つ線分をまとめる
    O(N^2)
    Parameters:
        segs (Iterable[Segment]): 線分のリスト (segs 自体は変更しない)
    Returns:
        merged (list[Segment]): まとめた後の線分のリスト。各線分の a は b より (x, y) が辞書順で小さい
    """
    res = [Segment(s.a, s.b) if _point_key(s.a) <= _point_key(s.b) else Segment(s.b, s.a) for s in segs]

    def merge(s: Segment, t: Segment) -> Segment | None:
        """\
        s, t をまとめた線分を返す。まとめられないなら None
        """
        if abs(cross(s.b - s.a, t.b - t.a)) > EPS:
            return None
        if abs(ccw(s.a, t.a, s.b)) == 1:
            return None
        if ccw(s.a, s.b, t.a) == ONLINE_FRONT or ccw(t.a, t.b, s.a) == ONLINE_FRONT:
            return None
        return Segment(min(s.a, t.a, key=_point_key), max(s.b, t.b, key=_point_key))

    i = 0
    while i < len(res):
        j = i + 1
        while j < len(res):
            merged = merge(res[i], res[j])
            if merged is None:
                j += 1
                continue
            # res[i] が伸びると、前に調べた線分ともまとめられるかもしれないので、最初から調べ直す
            res[i] = merged
            res[j] = res[-1]
            res.pop()
            j = i + 1
        i += 1
    return res


def segment_arrangement(segs: Sequence[Segment]) -> tuple[list[complex], list[list[int]]]:
    """\
    線分アレンジメント
    線分の端点と交点を頂点とし、線分上で隣り合う頂点どうしを辺で結んだグラフを作る
    同じ直線上で重なる線分があると辺が重複するので、先に merge_segments でまとめておく
    O(N^2 M) (M は頂点数, M = O(N^2))
    Parameters:
        segs (Sequence[Segment]): 線分のリスト
    Returns:
        points (list[complex]): 頂点の座標 (誤差 EPS 未満の点は 1 つにまとめる)
        graph (list[list[int]]): graph[v] は頂点 v と辺で結ばれた頂点番号のリスト
    """
    cand: list[complex] = []
    for i, s in enumerate(segs):
        cand.append(s.a)
        cand.append(s.b)
        for t in segs[i + 1 :]:
            cand.extend(crosspoint_segment_segment(s, t)[0])

    # x 座標順に見て、x の差が EPS 未満の点の中に近い点があれば同じ点とみなす
    points: list[complex] = []
    for p in sorted(cand, key=_point_key):
        k = len(points) - 1
        while k >= 0 and p.real - points[k].real < EPS and abs(p - points[k]) >= EPS:
            k -= 1
        if k < 0 or p.real - points[k].real >= EPS:
            points.append(p)

    graph: list[list[int]] = [[] for _ in points]
    for s in segs:
        d = s.b - s.a
        on = sorted(
            (v for v, p in enumerate(points) if intersect_segment_point(s, p)), key=lambda v: dot(points[v] - s.a, d)
        )
        for u, v in pairwise(on):
            graph[u].append(v)
            graph[v].append(u)
    return points, graph


# ---------- 引数の型で振り分ける関数 (C++ の多重定義の代わり) ----------
# intersect(s, t) のように図形を渡すと、型を見て上の関数を呼び分ける
# 引数の順番はどちらでもよい (intersect(p, l) は intersect_line_point(l, p) になる)
# Segment は Line を継承しているが、Segment として扱う

Shape = complex | Line | Circle


def _kind(x: object) -> str:
    """\
    図形の種類を 1 文字で返す (P: 点, S: 線分, L: 直線, C: 円)
    """
    # Segment は Line の子クラスなので、先に調べる
    if isinstance(x, Segment):
        return "S"
    if isinstance(x, Line):
        return "L"
    if isinstance(x, Circle):
        return "C"
    if isinstance(x, (complex, float, int)):
        return "P"
    raise TypeError(f"unsupported shape: {type(x).__name__}")


def _dispatch(table: dict, name: str, x: object, y: object):
    """\
    x, y の種類の組に対応する関数を table から探して呼ぶ (見つからなければ引数を入れ替えて探す)
    """
    kx, ky = _kind(x), _kind(y)
    f = table.get((kx, ky))
    if f is not None:
        return f(x, y)
    f = table.get((ky, kx))
    if f is not None:
        return f(y, x)
    raise TypeError(f"{name}() does not support ({type(x).__name__}, {type(y).__name__})")


_INTERSECT = {
    ("L", "P"): intersect_line_point,
    ("S", "P"): intersect_segment_point,
    ("L", "L"): intersect_line_line,
    ("L", "S"): intersect_line_segment,
    ("S", "S"): intersect_segment_segment,
    ("C", "P"): intersect_circle_point,
    ("C", "L"): intersect_circle_line,
    ("C", "S"): intersect_circle_segment,
    ("C", "C"): intersect_circle_circle,
}

_DISTANCE = {
    ("P", "P"): distance_point_point,
    ("L", "P"): distance_line_point,
    ("S", "P"): distance_segment_point,
    ("L", "L"): distance_line_line,
    ("L", "S"): distance_line_segment,
    ("S", "S"): distance_segment_segment,
}

_CROSSPOINT = {
    ("L", "L"): crosspoint_line_line,
    ("L", "S"): crosspoint_line_segment,
    ("S", "S"): crosspoint_segment_segment,
    ("C", "L"): crosspoint_circle_line,
    ("C", "S"): crosspoint_circle_segment,
    ("C", "C"): crosspoint_circle_circle,
}

_TANGENT = {
    ("C", "P"): tangent_circle_point,
    ("C", "C"): tangent_circle_circle,
}


def intersect(x: Shape, y: Shape) -> int:
    """\
    2 つの図形の共有点の個数を返す (共有点が無限にあるなら INF)
    (直線, 点), (線分, 点), (円, 点), (直線, 直線), (直線, 線分), (線分, 線分), (円, 直線), (円, 線分), (円, 円) に対応する
    円の周だけを図形とみなす (円の内部にある点・線分は共有点を持たない)
    Raises:
        TypeError: 対応していない図形の組のとき
    """
    return _dispatch(_INTERSECT, "intersect", x, y)


def distance(x: Shape, y: Shape) -> float:
    """\
    2 つの図形の距離を返す
    (点, 点), (直線, 点), (線分, 点), (直線, 直線), (直線, 線分), (線分, 線分) に対応する
    Raises:
        TypeError: 対応していない図形の組のとき
    """
    return _dispatch(_DISTANCE, "distance", x, y)


def crosspoint(x: Line | Circle, y: Line | Circle) -> tuple[list[complex], bool]:
    """\
    2 つの図形の交点を返す
    (直線, 直線), (直線, 線分), (線分, 線分), (円, 直線), (円, 線分), (円, 円) に対応する
    Returns:
        points (list[complex]): 交点のリスト (並び順は crosspoint_circle_line などを参照)
        infinite (bool): 共有点が無限にあるなら True (points は空)
    Raises:
        TypeError: 対応していない図形の組のとき
    """
    return _dispatch(_CROSSPOINT, "crosspoint", x, y)


def tangent(x: Circle | complex, y: Circle | complex) -> list[Line]:
    """\
    接線のリストを返す。各直線の a は (1 つ目の) 円との接点
    (円, 点) なら点を通る円の接線 (tangent_circle_point)
    (円, 円) なら共通接線 (tangent_circle_circle)
    Raises:
        TypeError: 対応していない図形の組のとき
    """
    return _dispatch(_TANGENT, "tangent", x, y)
