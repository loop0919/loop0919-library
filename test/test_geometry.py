import math
import random

import pytest

from library.geometry.geometry import (
    CLOCKWISE,
    COUNTER_CLOCKWISE,
    IN,
    INF,
    ON,
    ON_SEGMENT,
    ONLINE_BACK,
    ONLINE_FRONT,
    OUT,
    Circle,
    Line,
    Segment,
    area,
    area_polygon_circle,
    ccw,
    closest_pair,
    contains,
    convex_cut,
    convex_diameter,
    convex_hull,
    count_common_tangents,
    cross,
    crosspoint,
    crosspoint_circle_circle,
    crosspoint_circle_line,
    crosspoint_circle_segment,
    crosspoint_line_line,
    crosspoint_line_segment,
    crosspoint_segment_segment,
    distance,
    distance_line_line,
    distance_line_point,
    distance_line_segment,
    distance_point_point,
    distance_segment_point,
    distance_segment_segment,
    get_angle,
    get_signed_angle,
    get_signed_angle_line_line,
    intersect,
    intersect_circle_circle,
    intersect_circle_line,
    intersect_circle_point,
    intersect_circle_segment,
    intersect_line_line,
    intersect_line_point,
    intersect_line_segment,
    intersect_segment_point,
    intersect_segment_segment,
    is_convex,
    merge_segments,
    orthogonal,
    parallel,
    projection,
    reflection,
    rotate,
    segment_arrangement,
    tangent,
    tangent_circle_circle,
    tangent_circle_point,
)

TOL = 1e-6


def close(p, q, tol=TOL):
    """点 (または数) p, q が誤差 tol 以内で一致するか"""
    return abs(p - q) <= tol


def close_points(ps, qs, tol=TOL):
    """点のリストが、順番を除いて誤差 tol 以内で一致するか"""
    key = lambda p: (round(p.real, 6), round(p.imag, 6))  # noqa: E731
    return len(ps) == len(qs) and all(close(p, q, tol) for p, q in zip(sorted(ps, key=key), sorted(qs, key=key)))


def random_point(rng, lo=-5, hi=5):
    """格子点をランダムに選ぶ (一直線に並ぶ・重なるなどの退化が起きやすい)"""
    return complex(rng.randint(lo, hi), rng.randint(lo, hi))


def random_segment(rng, lo=-5, hi=5):
    while True:
        a, b = random_point(rng, lo, hi), random_point(rng, lo, hi)
        if a != b:
            return Segment(a, b)


def exact_ccw(a, b, c):
    """整数座標で誤差なしに ccw を計算する"""
    bx, by = int(b.real - a.real), int(b.imag - a.imag)
    cx, cy = int(c.real - a.real), int(c.imag - a.imag)
    cr = bx * cy - by * cx
    if cr > 0:
        return COUNTER_CLOCKWISE
    if cr < 0:
        return CLOCKWISE
    if bx * cx + by * cy < 0:
        return ONLINE_BACK
    if bx * bx + by * by < cx * cx + cy * cy:
        return ONLINE_FRONT
    return ON_SEGMENT


def exact_count_segment_segment(s, t):
    """整数座標で誤差なしに線分 s, t の共有点の個数を求める"""
    if not (
        exact_ccw(s.a, s.b, t.a) * exact_ccw(s.a, s.b, t.b) <= 0
        and exact_ccw(t.a, t.b, s.a) * exact_ccw(t.a, t.b, s.b) <= 0
    ):
        return 0
    d, e = s.b - s.a, t.b - t.a
    if int(d.real * e.imag - d.imag * e.real) != 0:
        return 1
    # 同じ直線上にある: s の向きへの射影 (|d| 倍したもの) で重なりを調べる
    ta = int(((t.a - s.a) * d.conjugate()).real)
    tb = int(((t.b - s.a) * d.conjugate()).real)
    lo, hi = max(0, min(ta, tb)), min(int(abs(d) ** 2 + 0.5), max(ta, tb))
    return INF if hi > lo else 1


def naive_distance_segment_point(s, p):
    """線分上で p に最も近い点を、媒介変数を [0, 1] に切り詰めて求める"""
    d = s.b - s.a
    t = ((p - s.a) * d.conjugate()).real / abs(d) ** 2
    return abs(s.a + d * min(1.0, max(0.0, t)) - p)


def circle_polygon(c, n=4096):
    """円を正 n 角形で近似する"""
    return [c.p + c.r * complex(math.cos(2 * math.pi * k / n), math.sin(2 * math.pi * k / n)) for k in range(n)]


def approx_area_convex_circle(poly, c):
    """反時計回りの凸多角形 poly と円 c の共通部分の面積を、円を多角形で近似して convex_cut で求める"""
    res = circle_polygon(c)
    for i in range(len(poly)):
        res = convex_cut(res, Line(poly[i - 1], poly[i]))
    return area(res)


def test_docstring_example():
    s = Segment(0 + 0j, 2 + 2j)
    t = Segment(0 + 2j, 2 + 0j)
    assert intersect(s, t) == 1
    assert crosspoint(s, t) == ([1 + 1j], False)
    assert distance(s, 3 + 3j) == math.sqrt(2)
    assert intersect(s, Segment(1 + 1j, 3 + 3j)) == INF == 1 << 60
    assert crosspoint(s, Segment(1 + 1j, 3 + 3j)) == ([], True)

    poly = convex_hull([0j, 2 + 0j, 1 + 1j, 2 + 2j, 0 + 2j])
    assert poly == [0j, 2 + 0j, 2 + 2j, 2j]
    assert area(poly) == 4.0

    c = Circle(0j, 1.0)
    assert crosspoint(c, Line(-2 + 0j, 2 + 0j)) == ([-1 + 0j, 1 + 0j], False)


# ---------- 点・直線 ----------


def test_repr():
    assert repr(Line(0j, 1 + 2j)) == "Line(0j, (1+2j))"
    assert repr(Segment(0j, 1j)) == "Segment(0j, 1j)"
    assert repr(Circle(1j, 2.0)) == "Circle(1j, 2.0)"


@pytest.mark.parametrize(("A", "B", "C"), [(1, 1, 2), (0, 2, 3), (2, 0, 3), (1, -2, 0), (3, 4, -5), (0, 1, 0)])
def test_line_from_equation(A, B, C):
    l = Line.from_equation(A, B, C)
    assert not close(l.a, l.b)
    for p in (l.a, l.b):
        assert close(A * p.real + B * p.imag, C)


def test_rotate():
    assert close(rotate(math.pi / 2, 1 + 0j), 1j)
    assert close(rotate(math.pi, 1 + 2j), -1 - 2j)
    assert close(rotate(-math.pi / 4, 1 + 1j), math.sqrt(2))


@pytest.mark.parametrize(
    ("a", "b", "c", "want"),
    [
        (1 + 0j, 0j, 1 + 1j, math.pi / 4),
        (1 + 1j, 0j, 1 + 0j, math.pi / 4),
        (1 + 0j, 0j, -1 + 0j, math.pi),
        (1 + 0j, 0j, -1j, math.pi / 2),
        (1 + 0j, 0j, 2 + 0j, 0.0),
        (2 + 2j, 1 + 1j, 1 + 3j, math.pi / 4),
    ],
)
def test_get_angle(a, b, c, want):
    assert close(get_angle(a, b, c), want)


@pytest.mark.parametrize(
    ("a", "b", "c", "want"),
    [
        (1 + 0j, 0j, 1 + 1j, math.pi / 4),
        (1 + 1j, 0j, 1 + 0j, -math.pi / 4),
        (1 + 0j, 0j, 1j, math.pi / 2),
        (1 + 0j, 0j, -1j, -math.pi / 2),
        (1 + 0j, 0j, -1 + 0j, math.pi),
        (-1 + 0j, 0j, 1 + 0j, math.pi),  # cross が -0.0 になるが、-π ではなく π を返す
        (1 + 0j, 0j, 2 + 0j, 0.0),
        (2 + 2j, 1 + 1j, 1 + 3j, math.pi / 4),
        (1 + 3j, 1 + 1j, 2 + 2j, -math.pi / 4),
    ],
)
def test_get_signed_angle(a, b, c, want):
    assert close(get_signed_angle(a, b, c), want)


@pytest.mark.parametrize("seed", range(3))
def test_get_signed_angle_random(seed):
    rng = random.Random(seed)
    for _ in range(1000):
        a, b, c = random_point(rng), random_point(rng), random_point(rng)
        if a == b or c == b:
            continue
        theta = get_signed_angle(a, b, c)
        assert -math.pi < theta <= math.pi
        assert close(abs(theta), get_angle(a, b, c))
        # ba を theta 回すと bc と同じ向きになる
        assert close(rotate(theta, (a - b) / abs(a - b)), (c - b) / abs(c - b)), (a, b, c)


@pytest.mark.parametrize(
    ("l", "m", "want"),
    [
        (Line(0j, 1 + 0j), Line(0j, 1j), math.pi / 2),
        (Line(0j, 1j), Line(0j, 1 + 0j), -math.pi / 2),
        (Line(0j, 1 + 0j), Line(0j, -1 + 1j), 3 * math.pi / 4),
        (Line(0j, 1 + 0j), Line(0j, -1 - 1j), -3 * math.pi / 4),
        (Line(0j, 1 + 0j), Segment(2 + 2j, 3 + 3j), math.pi / 4),
        (Segment(1j, 1 + 2j), Line(5 + 0j, 6 + 0j), -math.pi / 4),
    ],
)
def test_get_signed_angle_line_line(l, m, want):
    assert close(get_signed_angle_line_line(l, m), want)


def test_get_signed_angle_line_line_parallel():
    # 平行なら、同じ向きで 0、逆向きで π をちょうど返す
    assert get_signed_angle_line_line(Line(0j, 1 + 0j), Line(5j, 3 + 5j)) == 0.0
    assert get_signed_angle_line_line(Line(0j, 1 + 0j), Line(3 + 5j, 5j)) == math.pi
    assert get_signed_angle_line_line(Line(0j, -1 + 0j), Line(0j, 1 + 0j)) == math.pi
    assert get_signed_angle_line_line(Line(0j, 1 + 1j), Line(1 + 0j, 2 + 1j)) == 0.0
    # 0.1 + 0.2 は 0.3 よりわずかに大きいが、平行とみなす
    assert get_signed_angle_line_line(Line(0j, 0.3 + 0.3j), Line(0j, 0.1 + 0.2 + 0.3j)) == 0.0


def test_cross_dot():
    assert cross(1 + 0j, 1j) == 1
    assert cross(1j, 1 + 0j) == -1
    assert cross(2 + 4j, 1 + 2j) == 0


# AOJ CGL_1_C
@pytest.mark.parametrize(
    ("p", "want"),
    [
        (-1 + 1j, COUNTER_CLOCKWISE),
        (-1 - 1j, CLOCKWISE),
        (-1 + 0j, ONLINE_BACK),
        (0j, ON_SEGMENT),
        (3 + 0j, ONLINE_FRONT),
    ],
)
def test_ccw_aoj(p, want):
    assert ccw(0j, 2 + 0j, p) == want


@pytest.mark.parametrize("seed", range(5))
def test_ccw_random(seed):
    rng = random.Random(seed)
    for _ in range(1000):
        a, b, c = random_point(rng), random_point(rng), random_point(rng)
        if a != b:
            assert ccw(a, b, c) == exact_ccw(a, b, c), (a, b, c)


def test_ccw_tolerates_rounding():
    # 0.1 + 0.2 は 0.3 よりわずかに大きいが、線分の端点とみなす
    assert ccw(0j, 0.3 + 0j, 0.1 + 0.2 + 0j) == ON_SEGMENT
    assert intersect_segment_segment(Segment(0j, 0.3 + 0j), Segment(0.1 + 0.2 + 0j, 1 + 0j)) == 1


# AOJ CGL_2_A
def test_parallel_orthogonal():
    l = Line(0j, 3 + 0j)
    assert parallel(l, Line(2j, 3 + 2j))
    assert not orthogonal(l, Line(2j, 3 + 2j))
    assert orthogonal(l, Line(1 + 1j, 1 + 4j))
    assert not parallel(l, Line(1 + 1j, 1 + 4j))
    assert not parallel(l, Line(1 + 1j, 2 + 2j))
    assert not orthogonal(l, Line(1 + 1j, 2 + 2j))


# AOJ CGL_1_A, CGL_1_B
@pytest.mark.parametrize(
    ("l", "p", "proj", "refl"),
    [
        (Line(0j, 2 + 0j), -1 + 1j, -1 + 0j, -1 - 1j),
        (Line(0j, 2 + 0j), 0 + 1j, 0j, -1j),
        (Line(0j, 2 + 0j), 1 + 1j, 1 + 0j, 1 - 1j),
        (Line(0j, 3 + 4j), 2 + 5j, 3.12 + 4.16j, 4.24 + 3.32j),
    ],
)
def test_projection_reflection(l, p, proj, refl):
    assert close(projection(l, p), proj)
    assert close(reflection(l, p), refl)


def test_intersect_point():
    l = Line(0j, 2 + 2j)
    assert intersect_line_point(l, 1 + 1j) == 1
    assert intersect_line_point(l, 5 + 5j) == 1
    assert intersect_line_point(l, -3 - 3j) == 1
    assert intersect_line_point(l, 1 + 2j) == 0

    s = Segment(0j, 2 + 2j)
    assert intersect_segment_point(s, 1 + 1j) == 1
    assert intersect_segment_point(s, 0j) == 1
    assert intersect_segment_point(s, 2 + 2j) == 1
    assert intersect_segment_point(s, 3 + 3j) == 0
    assert intersect_segment_point(s, -1 - 1j) == 0
    assert intersect_segment_point(s, 1 + 0j) == 0


def test_intersect_line_line():
    l = Line(0j, 1 + 1j)
    assert intersect_line_line(l, Line(1j, 1 + 0j)) == 1
    assert intersect_line_line(l, Line(5 + 5j, 7 + 7j)) == INF  # 同じ直線
    assert intersect_line_line(l, Line(1j, 1 + 2j)) == 0  # 平行


def test_intersect_line_segment():
    l = Line(0j, 1 + 0j)
    assert intersect_line_segment(l, Segment(5 - 1j, 6 + 1j)) == 1
    assert intersect_line_segment(l, Segment(5 + 0j, 6 + 1j)) == 1  # 端点が直線上
    assert intersect_line_segment(l, Segment(5 + 0j, 6 + 0j)) == INF  # 直線上に乗っている
    assert intersect_line_segment(l, Segment(5 + 1j, 6 + 2j)) == 0
    assert intersect_line_segment(l, Segment(5 - 1j, 6 - 2j)) == 0
    assert intersect_line_segment(l, Segment(5 + 1j, 6 + 1j)) == 0  # 平行


# AOJ CGL_2_B
@pytest.mark.parametrize(
    ("s", "t", "want"),
    [
        (Segment(0j, 3 + 0j), Segment(1 + 1j, 2 - 1j), 1),
        (Segment(0j, 3 + 0j), Segment(3 + 1j, 3 - 1j), 1),
        (Segment(0j, 3 + 0j), Segment(3 - 2j, 5 + 0j), 0),
        (Segment(0j, 3 + 0j), Segment(1j, 3 + 1j), 0),  # 平行
        # 同じ直線上
        (Segment(0j, 3 + 0j), Segment(3 + 0j, 5 + 0j), 1),  # 端点で接する
        (Segment(0j, 3 + 0j), Segment(-1 + 0j, 0j), 1),
        (Segment(0j, 3 + 0j), Segment(1 + 0j, 2 + 0j), INF),  # 含む
        (Segment(0j, 3 + 0j), Segment(2 + 0j, 5 + 0j), INF),  # 一部が重なる
        (Segment(0j, 3 + 0j), Segment(3 + 0j, 0j), INF),  # 一致
        (Segment(0j, 3 + 0j), Segment(4 + 0j, 5 + 0j), 0),
        (Segment(0j, 3 + 0j), Segment(-2 + 0j, -1 + 0j), 0),
    ],
)
def test_intersect_segment_segment(s, t, want):
    assert intersect_segment_segment(s, t) == want
    assert intersect_segment_segment(t, s) == want


@pytest.mark.parametrize("seed", range(5))
def test_intersect_segment_segment_random(seed):
    rng = random.Random(seed)
    for _ in range(1000):
        s, t = random_segment(rng), random_segment(rng)
        assert intersect_segment_segment(s, t) == exact_count_segment_segment(s, t), (s, t)


# AOJ CGL_2_C
@pytest.mark.parametrize(
    ("s", "t", "want"),
    [
        (Segment(0j, 2 + 0j), Segment(1 + 1j, 1 - 1j), 1 + 0j),
        (Segment(0j, 1 + 1j), Segment(1j, 1 + 0j), 0.5 + 0.5j),
        (Segment(0j, 1 + 1j), Segment(1 + 0j, 1j), 0.5 + 0.5j),
    ],
)
def test_crosspoint_segment_segment(s, t, want):
    ps, inf = crosspoint_segment_segment(s, t)
    assert not inf
    assert len(ps) == 1 and close(ps[0], want)


@pytest.mark.parametrize(
    ("t", "want"),
    [
        (Segment(3 + 0j, 5 + 0j), ([3 + 0j], False)),  # 同じ直線上で端点が接する
        (Segment(-1 + 0j, 0j), ([0j], False)),
        (Segment(1 + 0j, 5 + 0j), ([], True)),  # 重なる
        (Segment(4 + 0j, 5 + 0j), ([], False)),  # 同じ直線上で離れている
        (Segment(1j, 3 + 1j), ([], False)),  # 平行
        (Segment(4 + 1j, 5 - 1j), ([], False)),  # 直線は交わるが線分は交わらない
    ],
)
def test_crosspoint_segment_segment_special(t, want):
    s = Segment(0j, 3 + 0j)
    assert crosspoint_segment_segment(s, t) == want
    assert crosspoint_segment_segment(t, s) == want


def test_crosspoint_line_line():
    l = Line(0j, 1 + 0j)
    ps, inf = crosspoint_line_line(l, Line(5 + 1j, 5 + 2j))  # 線分の外側で交わる
    assert not inf and len(ps) == 1 and close(ps[0], 5 + 0j)
    assert crosspoint_line_line(l, Line(1j, 1 + 1j)) == ([], False)  # 平行
    assert crosspoint_line_line(l, Line(3 + 0j, -2 + 0j)) == ([], True)  # 同じ直線


def test_crosspoint_line_segment():
    l = Line(0j, 1 + 0j)
    ps, inf = crosspoint_line_segment(l, Segment(5 + 1j, 6 - 1j))
    assert not inf and len(ps) == 1 and close(ps[0], 5.5 + 0j)
    ps, inf = crosspoint_line_segment(l, Segment(5 + 0j, 6 + 1j))  # 端点が直線上
    assert not inf and len(ps) == 1 and close(ps[0], 5 + 0j)
    assert crosspoint_line_segment(l, Segment(5 + 1j, 6 + 2j)) == ([], False)
    assert crosspoint_line_segment(l, Segment(5 + 1j, 6 + 1j)) == ([], False)  # 平行
    assert crosspoint_line_segment(l, Segment(5 + 0j, 6 + 0j)) == ([], True)  # 直線上


# AOJ CGL_2_D
@pytest.mark.parametrize(
    ("s", "t", "want"),
    [
        (Segment(0j, 1 + 0j), Segment(1j, 1 + 1j), 1.0),
        (Segment(0j, 1 + 0j), Segment(2 + 1j, 1 + 2j), math.sqrt(2)),
        (Segment(-1 + 0j, 1 + 0j), Segment(1j, -1j), 0.0),
    ],
)
def test_distance_segment_segment(s, t, want):
    assert close(distance_segment_segment(s, t), want)


@pytest.mark.parametrize("seed", range(5))
def test_distance_segment_random(seed):
    rng = random.Random(seed)
    for _ in range(500):
        s, t = random_segment(rng), random_segment(rng)
        p = random_point(rng)
        assert close(distance_segment_point(s, p), naive_distance_segment_point(s, p)), (s, p)
        if intersect_segment_segment(s, t):
            want = 0.0
        else:
            want = min(
                naive_distance_segment_point(s, t.a),
                naive_distance_segment_point(s, t.b),
                naive_distance_segment_point(t, s.a),
                naive_distance_segment_point(t, s.b),
            )
        assert close(distance_segment_segment(s, t), want), (s, t)


def test_distance_line():
    l = Line(0j, 1 + 0j)
    assert close(distance_line_point(l, 5 + 3j), 3.0)
    assert close(distance_line_point(l, -5 - 2j), 2.0)
    assert close(distance_line_line(l, Line(2j, 1 + 2j)), 2.0)
    assert close(distance_line_line(l, Line(2j, 1 + 3j)), 0.0)
    assert close(distance_line_segment(l, Segment(5 + 1j, 6 + 3j)), 1.0)
    assert close(distance_line_segment(l, Segment(5 + 1j, 6 - 3j)), 0.0)


def test_distance_segment_point():
    s = Segment(0j, 2 + 0j)
    assert close(distance_segment_point(s, 1 + 1j), 1.0)
    assert close(distance_segment_point(s, -3 + 4j), 5.0)
    assert close(distance_segment_point(s, 5 - 4j), 5.0)
    assert close(distance_segment_point(s, 1 + 0j), 0.0)


# ---------- 円 ----------


def test_intersect_circle_point_line():
    c = Circle(0j, 2.0)
    assert intersect_circle_point(c, 2j) == 1
    assert intersect_circle_point(c, 1j) == 0
    assert intersect_circle_point(c, 3j) == 0
    assert intersect_circle_line(c, Line(1j, 1 + 1j)) == 2
    assert intersect_circle_line(c, Line(2j, 1 + 2j)) == 1  # 接する
    assert intersect_circle_line(c, Line(3j, 1 + 3j)) == 0


# AOJ CGL_7_A
@pytest.mark.parametrize(
    ("c1", "c2", "tangents", "points"),
    [
        (Circle(1 + 1j, 1), Circle(6 + 2j, 2), 4, 0),
        (Circle(1 + 2j, 1), Circle(4 + 2j, 2), 3, 1),
        (Circle(1 + 2j, 1), Circle(3 + 2j, 2), 2, 2),
        (Circle(0j, 1), Circle(1 + 0j, 2), 1, 1),
        (Circle(0j, 1), Circle(0j, 2), 0, 0),
        (Circle(0j, 1), Circle(0.5 + 0j, 3), 0, 0),
        (Circle(1 + 1j, 2), Circle(1 + 1j, 2), INF, INF),  # 一致
    ],
)
def test_count_common_tangents_and_intersect_circle_circle(c1, c2, tangents, points):
    assert count_common_tangents(c1, c2) == tangents
    assert count_common_tangents(c2, c1) == tangents
    assert intersect_circle_circle(c1, c2) == points
    assert intersect_circle_circle(c2, c1) == points


# AOJ CGL_7_D
@pytest.mark.parametrize(
    ("l", "want"),
    [
        (Line(1j, 4 + 1j), [1 + 1j, 3 + 1j]),
        (Line(4 + 1j, 1j), [3 + 1j, 1 + 1j]),  # l.a から l.b の向きに並ぶ
        (Line(3 + 0j, 3 + 3j), [3 + 1j]),  # 接する
        (Line(5 + 0j, 5 + 3j), []),
    ],
)
def test_crosspoint_circle_line(l, want):
    got, inf = crosspoint_circle_line(Circle(2 + 1j, 1), l)
    assert not inf
    assert len(got) == len(want)
    assert all(close(p, q) for p, q in zip(got, want))


@pytest.mark.parametrize(
    ("s", "want"),
    [
        (Segment(-3 + 0j, 3 + 0j), [-2 + 0j, 2 + 0j]),  # 2 点で交わる
        (Segment(3 + 0j, -3 + 0j), [2 + 0j, -2 + 0j]),  # s.a に近い順
        (Segment(0j, 3 + 0j), [2 + 0j]),  # 片方の端点が内部
        (Segment(-1 + 0j, 1 + 0j), []),  # 内部に収まる
        (Segment(3 + 0j, 5 + 0j), []),  # 外部
        (Segment(-3 + 2j, 3 + 2j), [2j]),  # 接する
        (Segment(2 + 0j, 5 + 0j), [2 + 0j]),  # 端点が周上で、残りは外部
        (Segment(2 + 0j, 0j), [2 + 0j]),  # 端点が周上で、残りは内部
        (Segment(-2 + 0j, 2 + 0j), [-2 + 0j, 2 + 0j]),  # 両端が周上
    ],
)
def test_crosspoint_circle_segment(s, want):
    c = Circle(0j, 2)
    got, inf = crosspoint_circle_segment(c, s)
    assert not inf
    assert len(got) == len(want)
    assert all(close(p, q) for p, q in zip(got, want))
    assert intersect_circle_segment(c, s) == len(want)


# AOJ CGL_7_E
@pytest.mark.parametrize(
    ("c1", "c2", "want"),
    [
        (Circle(0j, 2), Circle(2 + 0j, 2), [1 + math.sqrt(3) * 1j, 1 - math.sqrt(3) * 1j]),
        (Circle(0j, 2), Circle(3j, 1), [2j]),  # 外接
        (Circle(0j, 1), Circle(1 + 0j, 2), [-1 + 0j]),  # 内接
        (Circle(0j, 1), Circle(5 + 0j, 2), []),  # 離れている
        (Circle(0j, 1), Circle(0.5 + 0j, 3), []),  # 含む
        (Circle(0j, 1), Circle(0j, 2), []),  # 中心が同じ
    ],
)
def test_crosspoint_circle_circle(c1, c2, want):
    for x, y in ((c1, c2), (c2, c1)):
        ps, inf = crosspoint_circle_circle(x, y)
        assert not inf
        assert close_points(ps, want)


def test_crosspoint_circle_circle_same():
    assert crosspoint_circle_circle(Circle(1j, 2), Circle(1j, 2)) == ([], True)


@pytest.mark.parametrize("seed", range(5))
def test_crosspoint_circle_random(seed):
    rng = random.Random(seed)
    for _ in range(300):
        c1 = Circle(random_point(rng), rng.randint(1, 4))
        c2 = Circle(random_point(rng), rng.randint(1, 4))
        s = random_segment(rng)
        for p in crosspoint_circle_circle(c1, c2)[0]:
            assert intersect_circle_point(c1, p) and intersect_circle_point(c2, p)
        for p in crosspoint_circle_line(c1, s)[0]:
            assert intersect_circle_point(c1, p) and intersect_line_point(s, p)
        for p in crosspoint_circle_segment(c1, s)[0]:
            assert intersect_circle_point(c1, p) and intersect_segment_point(s, p)


# AOJ CGL_7_F
@pytest.mark.parametrize(
    ("c", "p", "want"),
    [
        (Circle(2 + 2j, 2), 0j, [2j, 2 + 0j]),
        (Circle(2 + 2j, 2), -3 + 0j, [0.6206896552 + 3.4482758621j, 2 + 0j]),
        (Circle(0j, 1), 1j, [1j]),  # 周上
        (Circle(0j, 2), 1j, []),  # 内部
    ],
)
def test_tangent_circle_point(c, p, want):
    lines = tangent_circle_point(c, p)
    assert close_points([l.a for l in lines], want)
    for l in lines:
        assert intersect_circle_point(c, l.a)
        assert intersect_line_point(l, p)
        assert close(distance_line_point(l, c.p), c.r)


# AOJ CGL_7_G
@pytest.mark.parametrize(
    ("c1", "c2", "want"),
    [
        (
            Circle(1 + 1j, 1),
            Circle(6 + 2j, 2),
            [0.6153846154 + 1.9230769231j, 1 + 0j, 1.4183420913 + 1.9082895434j, 1.7355040625 + 0.3224796874j],
        ),
        (Circle(1 + 2j, 1), Circle(4 + 2j, 2), [0.6666666667 + 1.0571909584j, 0.6666666667 + 2.9428090416j, 2 + 2j]),
        (Circle(1 + 2j, 1), Circle(3 + 2j, 2), [0.5 + 1.1339745962j, 0.5 + 2.8660254038j]),
        (Circle(0j, 1), Circle(1 + 0j, 2), [-1 + 0j]),
        (Circle(0j, 1), Circle(0j, 2), []),
        # c1 の方が大きい
        (Circle(1 + 0j, 2), Circle(0j, 1), [-1 + 0j]),
        (Circle(6 + 2j, 2), Circle(1 + 1j, 1), None),
    ],
)
def test_tangent_circle_circle(c1, c2, want):
    lines = tangent_circle_circle(c1, c2)
    if want is not None:
        assert close_points([l.a for l in lines], want, 1e-8)
    assert len(lines) == count_common_tangents(c1, c2)
    for l in lines:
        assert intersect_circle_point(c1, l.a)
        assert close(distance_line_point(l, c1.p), c1.r)
        assert close(distance_line_point(l, c2.p), c2.r)


@pytest.mark.parametrize("seed", range(5))
def test_tangent_circle_circle_random(seed):
    rng = random.Random(seed)
    for _ in range(300):
        c1 = Circle(random_point(rng), rng.randint(1, 4))
        c2 = Circle(random_point(rng), rng.randint(1, 4))
        lines = tangent_circle_circle(c1, c2)
        if c1.p != c2.p:
            assert len(lines) == count_common_tangents(c1, c2), (c1, c2)
        for l in lines:
            assert intersect_circle_point(c1, l.a)
            assert close(distance_line_point(l, c1.p), c1.r)
            assert close(distance_line_point(l, c2.p), c2.r)


# ---------- 多角形 ----------


# AOJ CGL_3_A
def test_area():
    assert area([0j, 2 + 2j, -1 + 1j]) == 2.0
    assert area([0j, 1 + 1j, 1 + 2j, 2j]) == 1.5
    assert area([-1 + 1j, 2 + 2j, 0j]) == -2.0  # 時計回り
    assert area([]) == 0.0


# AOJ CGL_3_B
def test_is_convex():
    assert is_convex([0j, 3 + 1j, 2 + 3j, 3j])
    assert not is_convex([0j, 2 + 0j, 1 + 1j, 2 + 2j, 2j])
    assert is_convex([0j, 1 + 0j, 2 + 0j, 2 + 2j, 2j])  # 一直線に並ぶ頂点を含む
    assert not is_convex([3j, 2 + 3j, 3 + 1j, 0j])  # 時計回り


# AOJ CGL_3_C
@pytest.mark.parametrize(("p", "want"), [(2 + 1j, IN), (2j, ON), (3 + 2j, OUT), (0j, ON), (1.5 + 0.5j, ON)])
def test_contains_aoj(p, want):
    assert contains([0j, 3 + 1j, 2 + 3j, 3j], p) == want


@pytest.mark.parametrize(
    ("p", "want"),
    [
        (1 + 1j, IN),
        (3 + 1j, IN),
        (2 + 3j, OUT),  # 凹んだ部分
        (2 + 2j, ON),  # 凹んだ頂点
        (1 + 4j, ON),
        (5 + 2j, OUT),
        (-1 + 0j, OUT),  # 底辺の延長上
        (5 + 0j, OUT),
    ],
)
def test_contains_concave(p, want):
    # 凹型 (上辺の中央が下に凹んでいる)
    poly = [0j, 4 + 0j, 4 + 4j, 3 + 4j, 2 + 2j, 1 + 4j, 4j]
    assert contains(poly, p) == want
    assert contains(poly[::-1], p) == want


# AOJ CGL_4_A
def test_convex_hull_aoj():
    ps = [2 + 1j, 0j, 1 + 2j, 2 + 2j, 4 + 2j, 1 + 3j, 3 + 3j]
    # (2, 1) は辺 (0, 0)-(4, 2) 上にある
    assert convex_hull(ps) == [0j, 4 + 2j, 3 + 3j, 1 + 3j]
    assert convex_hull(ps, strict=False) == [0j, 2 + 1j, 4 + 2j, 3 + 3j, 1 + 3j]
    ps = [0j, 2 + 2j, 2j, 1j]
    assert convex_hull(ps) == [0j, 2 + 2j, 2j]
    assert convex_hull(ps, strict=False) == [0j, 2 + 2j, 2j, 1j]


def test_convex_hull_degenerate():
    assert convex_hull([]) == []
    assert convex_hull([1 + 1j, 1 + 1j]) == [1 + 1j]
    assert convex_hull([1j, 0j]) == [0j, 1j]
    line = [2 + 2j, 0j, 1 + 1j, 3 + 3j, 1 + 1j]
    assert convex_hull(line) == [0j, 3 + 3j]
    assert convex_hull(line, strict=False) == [0j, 1 + 1j, 2 + 2j, 3 + 3j]


def test_convex_hull_does_not_modify_input():
    ps = [2 + 2j, 0j, 2 + 0j, 2j, 1 + 1j]
    convex_hull(ps)
    assert ps == [2 + 2j, 0j, 2 + 0j, 2j, 1 + 1j]


@pytest.mark.parametrize("seed", range(20))
def test_convex_hull_random(seed):
    rng = random.Random(seed)
    ps = [random_point(rng, -4, 4) for _ in range(rng.randint(3, 40))]

    # strict: 狭義凸で、全点を含み、頂点は入力の点
    hull = convex_hull(ps)
    n = len(hull)
    if n >= 3:
        assert all(ccw(hull[i - 1], hull[i], hull[(i + 1) % n]) == COUNTER_CLOCKWISE for i in range(n))
        assert all(contains(hull, p) != OUT for p in ps)
    assert set(hull) <= set(ps)
    assert len(set(hull)) == n

    # 非 strict: 凸で、全点を含み、境界上の点をすべて頂点に持つ
    hull2 = convex_hull(ps, strict=False)
    n2 = len(hull2)
    if n >= 3:
        assert is_convex(hull2)
        assert all(contains(hull2, p) != OUT for p in ps)
        assert {p for p in ps if contains(hull, p) == ON} == set(hull2)
    assert set(hull) <= set(hull2) <= set(ps)
    assert len(set(hull2)) == n2
    assert hull2[0] == min(ps, key=lambda p: (p.real, p.imag))


# AOJ CGL_4_B
def test_convex_diameter_aoj():
    assert close(convex_diameter([0j, 4 + 0j, 2 + 2j]), 4.0)
    assert close(convex_diameter([0j, 1 + 0j, 1 + 1j, 1j]), math.sqrt(2))


def test_convex_diameter_small():
    assert convex_diameter([1 + 1j]) == 0.0
    assert close(convex_diameter([0j, 3 + 4j]), 5.0)


@pytest.mark.parametrize("seed", range(20))
@pytest.mark.parametrize("strict", [True, False])
def test_convex_diameter_random(seed, strict):
    rng = random.Random(seed)
    ps = [random_point(rng, -10, 10) for _ in range(rng.randint(2, 60))]
    want = max(abs(p - q) for p in ps for q in ps)
    assert close(convex_diameter(convex_hull(ps, strict)), want)


# AOJ CGL_4_C
def test_convex_cut_aoj():
    poly = [1 + 1j, 4 + 1j, 4 + 3j, 1 + 3j]
    assert close(area(convex_cut(poly, Line(2 + 0j, 2 + 4j))), 2.0)
    assert close(area(convex_cut(poly, Line(2 + 4j, 2 + 0j))), 4.0)


def test_convex_cut_edge_cases():
    poly = [0j, 2 + 0j, 2 + 2j, 2j]
    # 辺に沿って切る
    assert close(area(convex_cut(poly, Line(0j, 2 + 0j))), 4.0)
    assert convex_cut(poly, Line(2 + 0j, 0j)) == [0j, 2 + 0j]
    # 頂点を通る対角線で切ると、頂点が重複しない
    assert convex_cut(poly, Line(0j, 2 + 2j)) == [0j, 2 + 2j, 2j]
    # 多角形の外を通る
    assert convex_cut(poly, Line(5 + 0j, 5 + 1j)) == poly
    assert convex_cut(poly, Line(5 + 1j, 5 + 0j)) == []


@pytest.mark.parametrize("seed", range(20))
def test_convex_cut_random(seed):
    rng = random.Random(seed)
    poly = convex_hull([random_point(rng, -10, 10) for _ in range(20)])
    s = random_segment(rng, -10, 10)
    left = convex_cut(poly, s)
    right = convex_cut(poly, Line(s.b, s.a))
    assert close(area(left) + area(right), area(poly))
    assert area(left) >= -TOL and area(right) >= -TOL
    for p in left:
        assert ccw(s.a, s.b, p) != CLOCKWISE
        assert contains(poly, p) != OUT


# AOJ CGL_7_H
@pytest.mark.parametrize(
    ("poly", "r", "want"),
    [
        ([1 + 1j, 4 + 1j, 5 + 5j], 5, 4.639858417607),
        ([0j, -3 - 6j, 1 - 3j, 5 - 4j], 5, 11.787686807576),
    ],
)
def test_area_polygon_circle_aoj(poly, r, want):
    assert close(area_polygon_circle(poly, Circle(0j, r)), want, 1e-9)


def test_area_polygon_circle_cases():
    square = [-10 - 10j, 10 - 10j, 10 + 10j, -10 + 10j]
    # 円が多角形に含まれる
    assert close(area_polygon_circle(square, Circle(1 + 2j, 3)), 9 * math.pi)
    # 多角形が円に含まれる
    assert close(area_polygon_circle(square, Circle(0j, 100)), 400.0)
    # 辺で円が半分に切られる
    assert close(area_polygon_circle(square, Circle(10 + 0j, 2)), 2 * math.pi)
    # 角で円が 4 分の 1 になる
    assert close(area_polygon_circle(square, Circle(10 + 10j, 2)), math.pi)
    # 時計回りなら負
    assert close(area_polygon_circle(square[::-1], Circle(1 + 2j, 3)), -9 * math.pi)
    # 離れている
    assert close(area_polygon_circle(square, Circle(50 + 0j, 3)), 0.0)
    # 頂点が 3 つ未満
    assert area_polygon_circle([0j, 1j], Circle(0j, 1)) == 0.0


@pytest.mark.parametrize("seed", range(20))
def test_area_polygon_circle_convex_random(seed):
    rng = random.Random(seed)
    poly = convex_hull([random_point(rng, -10, 10) for _ in range(rng.randint(3, 15))])
    if len(poly) < 3:
        return
    c = Circle(random_point(rng, -10, 10), rng.uniform(0.5, 12))
    want = approx_area_convex_circle(poly, c)
    assert close(area_polygon_circle(poly, c), want, 1e-4 * max(1.0, want))


@pytest.mark.parametrize("seed", range(20))
def test_area_polygon_circle_concave_random(seed):
    # 偏角の順に点を並べて、凹んだ (星形の) 多角形を作る
    rng = random.Random(seed)
    n = rng.randint(3, 12)
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(n))
    poly = [
        complex(round(r * math.cos(t), 3), round(r * math.sin(t), 3))
        for t, r in ((t, rng.uniform(1, 10)) for t in angles)
    ]
    c = Circle(complex(rng.uniform(-8, 8), rng.uniform(-8, 8)), rng.uniform(0.5, 12))

    # 頂点 0 を中心に三角形に分け、向き付きで足し合わせる
    want = 0.0
    for i in range(1, n - 1):
        tri = [poly[0], poly[i], poly[i + 1]]
        sign = 1 if area(tri) > 0 else -1
        want += sign * approx_area_convex_circle(tri if sign > 0 else tri[::-1], c)
    assert close(area_polygon_circle(poly, c), want, 1e-4 * max(1.0, abs(want)))


# ---------- その他 ----------


# AOJ CGL_5_A
def test_closest_pair_aoj():
    assert close(closest_pair([0j, 1 + 0j]), 1.0)
    assert close(closest_pair([0j, 2 + 0j, 1 + 1j]), math.sqrt(2))


def test_closest_pair_edge_cases():
    assert closest_pair([1 + 1j, 5 + 5j, 1 + 1j]) == 0.0
    assert close(closest_pair([0j, 1j, 2j, 3j, 10j]), 1.0)  # x 座標がすべて同じ
    with pytest.raises(ValueError):
        closest_pair([1j])
    with pytest.raises(ValueError):
        closest_pair([])


@pytest.mark.parametrize("seed", range(20))
def test_closest_pair_random(seed):
    rng = random.Random(seed)
    n = rng.randint(2, 200)
    if seed % 2 == 0:
        ps = [random_point(rng, -30, 30) for _ in range(n)]
    else:
        ps = [complex(rng.uniform(-100, 100), rng.uniform(-100, 100)) for _ in range(n)]
    want = min(abs(ps[i] - ps[j]) for i in range(n) for j in range(i))
    assert closest_pair(ps) == want


def to_tuple(s):
    return (s.a, s.b)


def seg_key(t):
    return (t[0].real, t[0].imag, t[1].real, t[1].imag)


def test_merge_segments():
    segs = [Segment(1 + 0j, 0j), Segment(2 + 0j, 3 + 0j), Segment(1 + 0j, 2 + 0j)]
    assert [to_tuple(s) for s in merge_segments(segs)] == [(0j, 3 + 0j)]
    assert to_tuple(segs[0]) == (1 + 0j, 0j)  # 入力は変更しない

    # 包含・重なり・平行だが別の直線・交差
    segs = [
        Segment(0j, 4 + 4j),
        Segment(1 + 1j, 2 + 2j),
        Segment(3 + 3j, 6 + 6j),
        Segment(1j, 4 + 5j),
        Segment(4 + 0j, 0 + 4j),
    ]
    got = sorted((to_tuple(s) for s in merge_segments(segs)), key=seg_key)
    assert got == [(0j, 6 + 6j), (1j, 4 + 5j), (4j, 4 + 0j)]

    # 同じ直線上でも離れていればまとめない
    segs = [Segment(0j, 1j), Segment(2j, 3j)]
    assert sorted((to_tuple(s) for s in merge_segments(segs)), key=seg_key) == [(0j, 1j), (2j, 3j)]


@pytest.mark.parametrize("seed", range(20))
def test_merge_segments_random(seed):
    # 水平な線分だけを作り、区間の併合と比べる
    rng = random.Random(seed)
    segs = []
    for _ in range(rng.randint(1, 30)):
        y = rng.randint(0, 2)
        l, r = sorted(rng.sample(range(20), 2))
        segs.append(
            Segment(complex(r, y), complex(l, y)) if rng.random() < 0.5 else Segment(complex(l, y), complex(r, y))
        )

    want = []
    for y in range(3):
        intervals = sorted(
            (s.a.real, s.b.real) if s.a.real < s.b.real else (s.b.real, s.a.real) for s in segs if s.a.imag == y
        )
        merged: list[list[float]] = []
        for l, r in intervals:
            if merged and l <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], r)
            else:
                merged.append([l, r])
        want += [(complex(l, y), complex(r, y)) for l, r in merged]

    got = [to_tuple(s) for s in merge_segments(segs)]
    assert sorted(got, key=seg_key) == sorted(want, key=seg_key)


def adjacency(points, graph):
    """グラフを、座標の組の集合に直す"""
    return {frozenset((points[u], points[v])) for u in range(len(graph)) for v in graph[u]}


def test_segment_arrangement_cross():
    points, graph = segment_arrangement([Segment(0j, 2 + 2j), Segment(2j, 2 + 0j)])
    assert close_points(points, [0j, 2j, 1 + 1j, 2 + 0j, 2 + 2j])
    center = min(range(len(points)), key=lambda v: abs(points[v] - (1 + 1j)))
    assert sorted(len(g) for g in graph) == [1, 1, 1, 1, 4]
    assert len(graph[center]) == 4


def test_segment_arrangement_grid():
    # 井の字形: 端点 8 個と交点 4 個、各線分が 3 本の辺に分かれる
    segs = [
        Segment(1 + 0j, 1 + 3j),
        Segment(2 + 0j, 2 + 3j),
        Segment(1j, 3 + 1j),
        Segment(3 + 2j, 2j),
    ]
    points, graph = segment_arrangement(segs)
    assert len(points) == 12
    assert sum(len(g) for g in graph) == 2 * 12
    edges = adjacency(points, graph)
    assert frozenset((1 + 1j, 2 + 1j)) in edges
    assert frozenset((1 + 1j, 1 + 2j)) in edges
    assert frozenset((1 + 0j, 1 + 1j)) in edges
    assert frozenset((1 + 0j, 1 + 2j)) not in edges


def test_segment_arrangement_shared_points():
    # 3 本の線分が 1 点で交わる・端点で接する
    segs = [Segment(0j, 2 + 2j), Segment(2j, 2 + 0j), Segment(1 + 0j, 1 + 1j)]
    points, graph = segment_arrangement(segs)
    assert close_points(points, [0j, 2j, 1 + 0j, 1 + 1j, 2 + 0j, 2 + 2j])
    edges = adjacency(points, graph)
    assert frozenset((1 + 0j, 1 + 1j)) in edges
    assert len(edges) == 5


# ---------- 型で振り分ける関数 ----------

P = 1 + 1j
L = Line(0j, 2 + 0j)
L2 = Line(1 - 1j, 1 + 1j)
S = Segment(-1 - 1j, 2 + 2j)
S2 = Segment(0j, 2 + 1j)
C = Circle(1 + 0j, 1.5)
C2 = Circle(2 + 1j, 1.0)


@pytest.mark.parametrize(
    ("x", "y", "f"),
    [
        (L, P, intersect_line_point),
        (S, P, intersect_segment_point),
        (L, L2, intersect_line_line),
        (L, S, intersect_line_segment),
        (S, S2, intersect_segment_segment),
        (C, P, intersect_circle_point),
        (C, L, intersect_circle_line),
        (C, S, intersect_circle_segment),
        (C, C2, intersect_circle_circle),
    ],
)
def test_intersect_dispatch(x, y, f):
    assert intersect(x, y) == f(x, y)
    assert intersect(y, x) == f(x, y)


@pytest.mark.parametrize(
    ("x", "y", "f"),
    [
        (P, 4 + 5j, distance_point_point),
        (L, 3 + 2j, distance_line_point),
        (S, 5 + 0j, distance_segment_point),
        (L, Line(1j, 1 + 1j), distance_line_line),
        (L, Segment(1j, 2 + 3j), distance_line_segment),
        (S, Segment(3 + 0j, 4 + 0j), distance_segment_segment),
    ],
)
def test_distance_dispatch(x, y, f):
    assert distance(x, y) == f(x, y)
    assert distance(y, x) == f(x, y)


@pytest.mark.parametrize(
    ("x", "y", "f"),
    [
        (L, L2, crosspoint_line_line),
        (L, S, crosspoint_line_segment),
        (S, S2, crosspoint_segment_segment),
        (C, L, crosspoint_circle_line),
        (C, S, crosspoint_circle_segment),
        (C, C2, crosspoint_circle_circle),
    ],
)
def test_crosspoint_dispatch(x, y, f):
    assert crosspoint(x, y) == f(x, y)
    if f is not crosspoint_circle_circle:  # 円どうしは引数の順で交点の並びが変わる
        assert crosspoint(y, x) == f(x, y)


def test_tangent_dispatch():
    c = Circle(2 + 2j, 2)
    assert [to_tuple(l) for l in tangent(c, 0j)] == [to_tuple(l) for l in tangent_circle_point(c, 0j)]
    assert [to_tuple(l) for l in tangent(0j, c)] == [to_tuple(l) for l in tangent_circle_point(c, 0j)]
    assert [to_tuple(l) for l in tangent(C, C2)] == [to_tuple(l) for l in tangent_circle_circle(C, C2)]


def test_dispatch_treats_segment_as_segment():
    # Segment は Line の子クラスだが、線分として扱う
    s = Segment(0j, 1 + 0j)
    assert intersect(s, 5 + 0j) == 0
    assert intersect(Line(s.a, s.b), 5 + 0j) == 1
    assert distance(s, 3 + 0j) == 2.0
    assert distance(Line(s.a, s.b), 3 + 0j) == 0.0


def test_dispatch_accepts_int_and_float_points():
    assert intersect(L, 1) == 1
    assert distance(L, 1.5) == 0.0
    assert distance(3, 4j) == 5.0


def test_area_with_circle():
    square = [-10 - 10j, 10 - 10j, 10 + 10j, -10 + 10j]
    assert area(square, Circle(10 + 0j, 2)) == area_polygon_circle(square, Circle(10 + 0j, 2))


@pytest.mark.parametrize(
    ("f", "x", "y"),
    [
        (intersect, P, 2 + 2j),
        (distance, C, P),
        (distance, C, C2),
        (crosspoint, P, L),
        (tangent, L, P),
        (intersect, "a", L),
        (distance, [1, 2], P),
    ],
)
def test_dispatch_unsupported(f, x, y):
    with pytest.raises(TypeError):
        f(x, y)


def random_shape(rng, kind):
    if kind == "L":
        s = random_segment(rng, -3, 3)
        return Line(s.a, s.b)
    if kind == "S":
        return random_segment(rng, -3, 3)
    return Circle(random_point(rng, -3, 3), rng.randint(1, 3))


def on_shape(x, p):
    if isinstance(x, Segment):
        return intersect_segment_point(x, p) == 1
    if isinstance(x, Line):
        return intersect_line_point(x, p) == 1
    return intersect_circle_point(x, p) == 1


@pytest.mark.parametrize("kinds", ["LL", "LS", "SS", "CL", "CS", "CC"])
@pytest.mark.parametrize("seed", range(5))
def test_intersect_crosspoint_consistent(kinds, seed):
    # intersect の個数と crosspoint の交点の数が合い、交点が両方の図形上にある
    rng = random.Random(seed)
    for _ in range(300):
        x, y = random_shape(rng, kinds[0]), random_shape(rng, kinds[1])
        k = intersect(x, y)
        ps, inf = crosspoint(x, y)
        assert intersect(y, x) == k
        if k == INF:
            assert (ps, inf) == ([], True), (x, y)
        else:
            assert not inf and len(ps) == k, (x, y, ps)
        for p in ps:
            assert on_shape(x, p) and on_shape(y, p), (x, y, p)
