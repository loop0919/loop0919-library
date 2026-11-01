# loop0919-library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

loop0919 の競技プログラミング用 Python ライブラリです。
各実装は [pytest](https://docs.pytest.org/) のユニットテストで動作を確かめています。

## 収録内容

### データ構造

- [Deque](library/data_structure/deque.py): 添字アクセスができる両端キュー。両端への追加・削除がならし O(1)、添字アクセスが O(1)

### 木

- [LowestCommonAncestor](library/tree/lca.py): ダブリングで最小共通祖先 (LCA) を求める。前計算 O(N log N)、クエリ O(log N)。2 頂点間の距離や、何世代か上の祖先も求められる

### 数学

- [is_prime](library/math/is_prime.py): Miller-Rabin 法による素数判定 (0 <= n <= 2\*\*64)

### 文字列

- [RollingHash](library/string/rolling_hash.py): 法 2\*\*61 - 1 のローリングハッシュ。O(N) の前計算のあと、区間のハッシュ値を O(1) で求める

### 幾何

- [geometry](library/geometry/geometry.py): 点を複素数 `complex` で表す幾何ライブラリ。誤差 `EPS` (= 1e-8) まで許して判定する
  - 基本: 内積・外積、回転、角度 (`get_angle`, `get_signed_angle`, `get_signed_angle_line_line`)、`ccw`、平行・垂直判定、射影・反射
  - 図形どうし: 交差判定 `intersect`、距離 `distance`、交点 `crosspoint`、接線 `tangent`。点・直線・線分・円の組み合わせに対応する
  - 多角形: 面積、凸性判定、点の内外判定、凸包、凸多角形の切断、凸多角形の直径、多角形と円の共通部分の面積
  - その他: 最近点対、同じ直線上の線分の併合、線分アレンジメント
- [arg_cmp](library/geometry/arg_cmp.py): 偏角ソート用の比較関数。整数だけで計算するので誤差が出ない。`cmp_sort` や `cmp_to_key` に渡して使う

### その他

- [cmp_sort](library/misc/cmp_sort.py): 比較関数による安定ソート。PyPy では `cmp_to_key` を使うより 10 倍ほど速い (N = 2 \* 10\*\*5)

## ディレクトリ構成

```
.
├── library/             # ライブラリ本体
│   ├── data_structure/
│   ├── tree/
│   ├── math/
│   ├── string/
│   ├── geometry/
│   └── misc/
├── test/                # ユニットテスト (test_*.py)
├── pyproject.toml       # 依存パッケージとツールの設定
├── uv.lock              # 依存パッケージのバージョンを固定するファイル
└── LICENSE.txt
```

## 使い方

ジャッジ環境にはこのライブラリが入っていないので、提出するときは使うモジュールの中身をコードに貼り付けてください。

手元で試すときは、リポジトリのルートを `PYTHONPATH` に追加すると `import` できます。

```sh
git clone https://github.com/loop0919/loop0919-library.git
export PYTHONPATH="/path/to/loop0919-library:$PYTHONPATH"
```

```python
# 例: Deque を使う場合
from library.data_structure.deque import Deque
```

## テスト

テストは `test/` に `test_<モジュール名>.py` という名前で置きます。

```python
# test/test_deque.py
from library.data_structure.deque import Deque


def test_append_pop():
    dq = Deque([1, 2])
    dq.appendleft(0)
    assert list(dq) == [0, 1, 2]
    assert dq.pop() == 2
```

依存パッケージは [uv](https://docs.astral.sh/uv/) で管理しています。
リポジトリのルートで次のコマンドを実行します。

```sh
uv sync                                      # 依存パッケージと開発用ツールを入れる
uv run python -m pytest                      # すべてのテストを実行
uv run python -m pytest test/test_deque.py   # 指定したファイルだけ実行
```

`python -m pytest` で起動すると、カレントディレクトリが `sys.path` に入るので `library` を `import` できます。
`uv run pytest` で起動すると `library` を `import` できずにエラーになるので注意してください。

## ライセンス

[MIT License](LICENSE.txt)
