# biisan

biisan（ビーサン）は、reStructuredText または Markdown で書いたブログを静的な HTML に変換するサイトジェネレーターです。文書をモデルオブジェクトへ変換し、差し替え可能な Jinja テンプレートで出力します。

[English](README.md)

## 動作環境

- Python 3.11 以降

## インストール

仮想環境を作成し、PyPI からインストールします。

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install biisan
```

## サイトを作る

サイトのプロジェクトを置きたいディレクトリで初期化コマンドを実行します。

```console
python -m biisan.main
```

次の構成が作成されます。

```text
biisan_data/
├── data/
│   ├── biisan_local_settings.py
│   ├── blog/
│   ├── extra/
│   │   └── about.rst
│   └── templates/
└── out/
```

reStructuredText の記事は `biisan_data/data/blog/` に置きます。

```rst
最初の記事
==========

:slug: first-entry
:date: 2026-09-19 13:00
:author: あなたの名前

こんにちは。
```

Markdown の記事では YAML front matter にメタデータを書きます。

```markdown
---
slug: markdown-entry
date: 2026-09-19 14:00
author: あなたの名前
---

# Markdown の記事

こんにちは、Markdown。
```

`data` ディレクトリからサイトを生成します。

```console
cd biisan_data/data
export BIISAN_SETTINGS_MODULE=biisan_local_settings
python -m biisan.generate
```

HTML、RSS フィード、サイトマップは `biisan_data/out/` 以下に出力されます。記事の URL は各記事の `date` と `slug` から決まります。

## カスタマイズ

タイトル、ベース URL、言語、出力先、並列処理数、プロセッサー、ディレクティブは `biisan_local_settings.py` で変更できます。組み込みテンプレートと同じ相対パスでテンプレートを `data/templates/` に置くと、そのテンプレートを優先して使用します。

reStructuredText の追加 docinfo と Markdown front matter の追加項目は、組み込み属性と名前が重複しない限り、テンプレートから story オブジェクトの属性として参照できます。

## 開発

開発環境とロックファイルの管理には [uv](https://docs.astral.sh/uv/) を使います。

```console
uv sync --locked
uv run pytest
uv run ruff format --check src tests
uv run ruff check src tests
uv run pyrefly check
uv build
uv run twine check dist/*
```

テストは Python 3.11〜3.14 で実行します。

## ライセンス

MIT
