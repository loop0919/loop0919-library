import random

import pytest

from library.tree.lca import LowestCommonAncestor

# 手で計算した木 (括弧内は親との辺の重み)
#
#         0
#       /   \
#     1(2)  2(5)
#    /  \      \
#   3(1) 4(3)  5(4)
#   |
#   6(7)
EDGES = [(0, 1, 2), (0, 2, 5), (1, 3, 1), (1, 4, 3), (2, 5, 4), (3, 6, 7)]


def build_sample(root: int = 0) -> LowestCommonAncestor:
    lca = LowestCommonAncestor(7)
    for u, v, w in EDGES:
        lca.add_edge(u, v, w)
    lca.build(root)
    return lca


@pytest.mark.parametrize(
    ("u", "v", "want"),
    [(6, 4, 1), (4, 6, 1), (6, 5, 0), (3, 6, 3), (6, 3, 3), (4, 4, 4), (5, 2, 2), (0, 6, 0)],
)
def test_lca(u, v, want):
    assert build_sample().lca(u, v) == want


@pytest.mark.parametrize(("u", "v", "want"), [(6, 4, 11), (6, 5, 19), (3, 3, 0), (0, 5, 9)])
def test_distance(u, v, want):
    assert build_sample().distance(u, v) == want


@pytest.mark.parametrize(("v", "want"), [(6, 3), (1, 0), (0, -1)])
def test_parent(v, want):
    assert build_sample().parent(v) == want


@pytest.mark.parametrize(("gen", "want"), [(0, 6), (1, 3), (2, 1), (3, 0)])
def test_ancestor(gen, want):
    assert build_sample().ancestor(6, gen) == want


def test_ancestor_beyond_root_returns_minus_one():
    assert build_sample().ancestor(6, 4) == -1


def test_build_with_other_root():
    lca = build_sample(root=3)
    assert lca.lca(0, 4) == 1
    assert lca.lca(6, 5) == 3
    assert lca.parent(3) == -1
    assert lca.parent(1) == 3
    assert lca.ancestor(5, 4) == 3


def test_rebuild_with_other_root():
    lca = build_sample(root=0)
    lca.build(root=3)
    assert lca.lca(6, 5) == 3
    assert lca.parent(3) == -1
    assert lca.parent(0) == 1


def test_long_path():
    # 0 - 1 - ... - 99 の一直線の木で、ダブリングの全段を使う
    n = 100
    lca = LowestCommonAncestor(n)
    for i in range(n - 1):
        lca.add_edge(i, i + 1)
    lca.build()
    assert lca.lca(99, 50) == 50
    assert lca.distance(99, 0) == 99
    assert lca.ancestor(99, 99) == 0
    assert lca.ancestor(99, 64) == 35
    assert lca.ancestor(99, 100) == -1


def test_single_vertex():
    lca = LowestCommonAncestor(1)
    lca.build()
    assert lca.lca(0, 0) == 0
    assert lca.distance(0, 0) == 0
    assert lca.parent(0) == -1


def naive_tree(n, edges, root):
    """親・深さ・根からの距離を素朴に求める"""
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    parent, depth, dist = [-1] * n, [0] * n, [0] * n
    seen = [False] * n
    seen[root] = True
    queue = [root]
    for now in queue:
        for to, w in adj[now]:
            if not seen[to]:
                seen[to] = True
                parent[to], depth[to], dist[to] = now, depth[now] + 1, dist[now] + w
                queue.append(to)
    return parent, depth, dist


def naive_lca(parent, depth, u, v):
    while depth[u] > depth[v]:
        u = parent[u]
    while depth[v] > depth[u]:
        v = parent[v]
    while u != v:
        u, v = parent[u], parent[v]
    return u


@pytest.mark.parametrize("seed", range(30))
def test_random_tree(seed):
    rng = random.Random(seed)
    n = rng.randint(1, 60)
    root = rng.randrange(n)
    edges = [(rng.randrange(i), i, rng.randint(0, 10)) for i in range(1, n)]
    perm = list(range(n))
    rng.shuffle(perm)
    edges = [(perm[u], perm[v], w) for u, v, w in edges]

    lca = LowestCommonAncestor(n)
    for u, v, w in edges:
        lca.add_edge(u, v, w)
    lca.build(root)
    parent, depth, dist = naive_tree(n, edges, root)

    for u in range(n):
        assert lca.parent(u) == parent[u]
        for v in range(n):
            a = naive_lca(parent, depth, u, v)
            assert lca.lca(u, v) == a
            assert lca.distance(u, v) == dist[u] + dist[v] - 2 * dist[a]
        x = u
        for gen in range(depth[u] + 1):
            assert lca.ancestor(u, gen) == x
            x = parent[x]
        assert lca.ancestor(u, depth[u] + 1) == -1
