# loop0919-library

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE.txt)

loop0919 の競技プログラミング用 Python ライブラリです。
各実装は [pytest](https://docs.pytest.org/) のユニットテストで動作を確かめています。

## 収録内容

### データ構造

- 準備中

### グラフ

- 準備中

### 数学

- 準備中

### 文字列

- 準備中

### その他

- 準備中

## ディレクトリ構成

```
.
├── library/             # ライブラリ本体
│   ├── data_structure/
│   ├── graph/
│   ├── math/
│   ├── string/
│   └── misc/
├── test/                # ユニットテスト (test_*.py)
├── pyproject.toml       # 依存パッケージとツールの設定
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
# 例: Union-Find を使う場合
from library.data_structure.union_find import UnionFind
```

## テスト

テストは `test/` に `test_<モジュール名>.py` という名前で置きます。

```python
# test/test_union_find.py
from library.data_structure.union_find import UnionFind


def test_merge():
    uf = UnionFind(4)
    uf.merge(0, 1)
    assert uf.same(0, 1)
    assert not uf.same(0, 2)
```

依存パッケージは [uv](https://docs.astral.sh/uv/) で管理しています。
リポジトリのルートで次のコマンドを実行します。

```sh
uv sync                                          # 依存パッケージと開発用ツールを入れる
uv run python -m pytest                          # すべてのテストを実行
uv run python -m pytest test/test_union_find.py  # 指定したファイルだけ実行
```

`python -m pytest` で起動すると、カレントディレクトリが `sys.path` に入るので `library` を `import` できます。
`uv run pytest` で起動すると `library` を `import` できずにエラーになるので注意してください。

## ライセンス

[MIT License](LICENSE.txt)
