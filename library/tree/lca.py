# ref: https://github.com/loop0919/loop0919-library/blob/main/library/tree/lca.py


class LowestCommonAncestor:
    """\
    Lowest Common Ancestor (LCA)
    ---
    木に対する最小共通祖先をダブリングで求めるデータ構造
    前計算 O(N log N), クエリ O(log N)

    Usage::

        # 辺: 0-1, 0-2, 1-3 (重み 10), 1-4
        lca = LowestCommonAncestor(5)
        lca.add_edge(0, 1)
        lca.add_edge(0, 2)
        lca.add_edge(1, 3, 10)
        lca.add_edge(1, 4)
        lca.build(root=0)

        print(lca.lca(3, 4))
        # => 1

        print(lca.distance(3, 2))
        # => 12

        print(lca.ancestor(3, 2))
        # => 0

        print(lca.ancestor(3, 3))
        # => -1 (根より上)
    """

    _n: int
    _log: int
    _edges: list[list[tuple[int, int]]]

    _parent: list[int]
    _depth: list[int]
    _distance: list[int]
    _doubling: list[list[int]]

    def __init__(self, n: int):
        """\
        木の頂点数 n を指定して初期化する
        Parameters:
            n (int): 木の頂点数
        """
        self._n = n
        self._log = max(1, (n - 1).bit_length())
        self._edges = [[] for _ in range(n)]

    def add_edge(self, u: int, v: int, w: int = 1) -> None:
        """\
        u, v 間に重み w の辺を追加する
        Parameters:
            u (int): 辺の片方の頂点
            v (int): 辺のもう片方の頂点
            w (int): 辺の重み
        """
        self._edges[u].append((v, w))
        self._edges[v].append((u, w))

    def build(self, root: int = 0) -> None:
        """\
        根を root にした木を構築する
        Parameters:
            root (int): 根の頂点番号
        """
        parent = [-1] * self._n
        depth = [0] * self._n
        distance = [0] * self._n

        stack = [root]
        while stack:
            now = stack.pop()
            for to, w in self._edges[now]:
                if to == parent[now]:
                    continue
                parent[to] = now
                depth[to] = depth[now] + 1
                distance[to] = distance[now] + w
                stack.append(to)

        # doubling[k][v]: v から 2**k 世代上の祖先
        # 根の親を根自身にしておくと、根より上に辿っても根で止まる
        up = parent[:]
        up[root] = root
        doubling = [up]
        for _ in range(self._log - 1):
            up = [up[p] for p in up]
            doubling.append(up)

        self._parent = parent
        self._depth = depth
        self._distance = distance
        self._doubling = doubling

    def lca(self, u: int, v: int) -> int:
        """\
        u, v の最小共通祖先を求める
        Parameters:
            u (int): 頂点 u
            v (int): 頂点 v
        Returns:
            lca (int): u, v の最小共通祖先
        """
        # u の深さを v の深さ以下になるよう調整し、v の深さを u に合わせる
        if self._depth[u] > self._depth[v]:
            u, v = v, u
        v = self.ancestor(v, self._depth[v] - self._depth[u])

        # この時点で一致すれば、それが解
        if u == v:
            return u

        # u, v がギリギリ一致しないよう親方向に辿る
        for up in reversed(self._doubling):
            if up[u] != up[v]:
                u, v = up[u], up[v]

        # 最後に 1 ステップ親方向に辿った頂点が解
        return self._parent[u]

    def distance(self, u: int, v: int) -> int:
        """\
        u, v 間の距離を求める
        Parameters:
            u (int): 頂点 u
            v (int): 頂点 v
        Returns:
            dist (int): u, v 間の最短距離の長さ
        """
        return self._distance[u] + self._distance[v] - 2 * self._distance[self.lca(u, v)]

    def parent(self, v: int) -> int:
        """\
        v の親を求める
        Parameters:
            v (int): 頂点 v
        Returns:
            parent (int): 頂点 v の親。v が根のときは -1
        """
        return self._parent[v]

    def ancestor(self, v: int, gen: int) -> int:
        """\
        v から gen 世代上の祖先を求める (gen = 0 なら v 自身)
        Parameters:
            v (int): 頂点 v
            gen (int): 何世代上か (0 以上)
        Returns:
            ancestor (int): 祖先の頂点番号。根より上を指定したときは -1
        """
        assert gen >= 0
        if gen > self._depth[v]:
            return -1

        for k, up in enumerate(self._doubling):
            if (gen >> k) & 1:
                v = up[v]
        return v
