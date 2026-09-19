# biisan

biisan（ビーサン）は、reStructuredText または Markdown で書いたブログを静的な HTML に変換するサイトジェネレーターです。文書をモデルオブジェクトへ変換し、差し替え可能な Jinja テンプレートで出力します。

[English](README.md)

## 動作環境

- Python 3.11 以降

## 主な機能

- reStructuredText と GitHub Flavored Markdown の記事を読み込む
- 差し替え可能な Jinja テンプレートでページを生成する
- ブログトップ、月別アーカイブ、全記事一覧、RSS、サイトマップを生成する
- 記事のカテゴリーごとに RSS を生成する
- 記事へ任意のメタデータを追加し、テンプレートから参照する
- Jinja の独自フィルターとグローバル関数を登録する
- 記事を並列に解析し、SHA-256 キャッシュで変更のないページの再出力を省く

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
:category: notes

こんにちは。
```

Markdown の記事では YAML front matter にメタデータを書きます。

```markdown
---
slug: markdown-entry
date: 2026-09-19 14:00
author: あなたの名前
category: notes
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

記事の URL は各記事の `date` と `slug` から決まります。

Markdown では見出し、段落、強調、リンク、画像、リスト、引用、コードブロック、表、区切り線、インラインおよびブロック HTML を利用できます。HTML は生成ページへそのまま出力されるため、信頼できる執筆者の入力に限って使用してください。

## 生成されるファイル

ビルドすると `biisan_data/out/` 以下に次のページが生成されます。

| パス | 内容 |
| --- | --- |
| `/index.html` | サイトトップ |
| `/blog/index.html` | 新着記事とアーカイブへのリンク |
| `/blog/all/index.html` | 全記事一覧 |
| `/blog/YYYY/MM/index.html` | 月別アーカイブ |
| `/blog/YYYY/MM/DD/slug/index.html` | 記事ページ |
| `/api/feed/index.xml` | 新着記事の RSS |
| `/api/feed/category/index.xml` | カテゴリー別 RSS |
| `/api/google_sitemaps/index.xml` | サイトマップ |
| `/name/index.html` | `about.rst` などの追加ページ |

`category: notes` を指定した記事がある場合は、`/api/feed/notes/index.xml` が生成されます。各 RSS に含める記事数は `latest_list_count` で指定します。

記事ページと追加ページには `.biisan.raw.sha256` も作成されます。次回のビルドでは、テンプレートによるレンダリング結果が変わっていなければ、HTML の圧縮と書き込みを省きます。

## カスタマイズ

サイトの設定は `biisan_local_settings.py` で変更します。よく使う設定は次のとおりです。

| 設定 | 用途 |
| --- | --- |
| `blog.title` | サイトのタイトル |
| `blog.base_url` | RSS とサイトマップで使う絶対 URL |
| `blog.language` | RSS の言語コード |
| `dir.output` | 出力先ディレクトリ |
| `timezone` | 記事日時へ設定するタイムゾーン |
| `latest_list_count` | 新着一覧と RSS に含める記事数 |
| `multiprocess` | 文書解析に使うプロセス数 |
| `extra` | `data/extra/` に置く追加 `.rst` ページの名前 |
| `custom_filters` | Jinja フィルター名と呼び出し可能オブジェクトの対応 |
| `template_functions` | Jinja グローバル名と呼び出し可能オブジェクトの対応 |

組み込みテンプレートと同じ相対パスでテンプレートを `data/templates/` に置くと、そのテンプレートを優先して使用します。初期化時に生成される設定では、このディレクトリが組み込みテンプレートより先に探索されます。

reStructuredText の追加 docinfo と Markdown front matter の追加項目は、組み込み属性と名前が重複しない限り、テンプレートから story オブジェクトの属性として参照できます。

例えば `category` は記事テンプレートから `element.category` として参照できます。任意項目を参照する前に、項目の有無を確認してください。

```jinja2
{% if element.has_additional_meta("og_image") %}
  <meta property="og:image" content="{{ element.og_image }}">
{% endif %}
```

## 開発

開発環境とロックファイルの管理には [uv](https://docs.astral.sh/uv/) を使います。依存解決では、公開から7日未満の配布物を候補から除外します。

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
