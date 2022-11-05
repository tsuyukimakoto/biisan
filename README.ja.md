# biisan

biisan（ビーサン）は、[reStructuredText](http://docutils.sourceforge.net/rst.html)で文書を記述できるスタティックサイトジェネレーターです。

## 特徴 Feature

- reStructuredTextの構造をオブジェクトの構造に変換し、reStructuredTextの[ディレクティブ](http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt)ごとにjinja2のテンプレートでhtmlに出力します
- biisanで対応しているディレクティブに関してはデフォルトのテンプレートが付属しますが、設定で探索先を設定すると利用するテンプレートを差し替えられます
- ディレクティブからオブジェクトへの変換プロセッサーも設定で任意のプロセッサーを差し替えられます
- 対応していないディレクティブの処理も差し替えと同様の仕組みで対応可能です
- 新しいディレクティブの定義も容易です
- reStructuredTextの構造をオブジェクトへ変換する処理はmultiprocessingで並行して行われます

## クイックスタート

### インストール

pipでインストールできます。同時に依存するライブラリーもインストールされますので、綺麗に消せるようにしておきたい場合には venv を用いて仮想環境を作ってインストールすると良いかもしれません。

```
$ pip install biisan
```

### イニシャライズ

biisanの基本構造と、設定ファイルを生成します。実行したフォルダ直下に `biisan_data` というフォルダができます。

`ブログタイトル`、 `ベースとなるURL`、 `言語コード` を聞かれるので答えます。あとから設定ファイルで変更可能です。

```
$ python -m biisan.main
? What's your blog title  ブログタイトル
? input your blog base url. like https://www.tsuyukimakoto.com  http:localhost
? input your blog language like ja  ja

        Always set environment variable BIISAN_SETTINGS_MODULE to biisan_local_settings like bellow.

        $ export BIISAN_SETTINGS_MODULE=biisan_local_settings

```

最後にbiisanを使うときに必ず必要な環境変数について出力されます。biisanを利用する際には必ず必要な環境変数です。

[glueplate](https://pypi.org/project/glueplate/) という設定フレームワークの設定です。

### 最初のエントリー

生成されたフォルダの中身を確認してみましょう。

```
$ cd biisan_data
$ tree
.
├── data
│   ├── biisan_local_settings.py
│   ├── blog
│   ├── extra
│   │   └── about.rst
│   └── templates
└── out
```

`biisan_data`フォルダの中に`data`と`out`という2つのフォルダがあります。

- data

    - biisan_local_settings.py

        設定ファイル。[大元の設定ファイル](https://github.com/tsuyukimakoto/biisan/blob/master/biisan/biisan_settings.py)の設定に追加したり上書きしたりしています。

    - blog

        この中にreStructuredTextのファイルを置きます。整理しやすいようにフォルダを作ると良いでしょう。blogフォルダの中のフォルダ構成は出力されるURLのpathとは関係ありません。

    - extra

        日付ベースのエントリーとは別のページを作りたい場合にファイルを置きます。aboutは標準で置かれて設定されています。
        新しく追加した場合には設定ファイル(data/biisan_local_settings.py)にGLUE_PLATE_PLUS_BEFORE_extraという定義を追加します。

        たとえば imusing.rst というファイルを置いた場合には `data/biisan_local_settings.py` に `GLUE_PLATE_PLUS_BEFORE_extra` を次のように定義します。

        ```
        #省略

        settings = _(
            # 省略
            multiprocess = 8,
            GLUE_PLATE_PLUS_BEFORE_extra = [
                'imusing',
            ],
        )
        ```

        これはglueplateの仕組みで、[大元の設定ファイル](https://github.com/tsuyukimakoto/biisan/blob/master/biisan/biisan_settings.py)にある `extra` という設定の前に ['imusing',] を追加するという指定です。

        [実際の設定](https://github.com/tsuyukimakoto/tsuyukimakoto.com/blob/master/data/biisan_local_settings.py#L19) も参照してみてください。

    - templates

        上書きしたいテンプレートを置きます。 GLUE_PLATE_PLUS_BEFORE_extra と同様に設定ファイルに `GLUE_PLATE_PLUS_BEFORE_template_dirs` が定義されているため、まずこのフォルダからテンプレートファイルを探し始めます。

- out

    このフォルダにhtmlが静的に出力されます。

### 今度こそ最初のエントリ

`data/blog`の中にmy_first_entry.rstというファイルで以下のように保存してみましょう。ファイル名は拡張子が .rst であればその前はなんでも構いません。

```
最初のエントリです
=========================================================

:slug: my_first_biisan_entry
:date: 2019-05-05 13:00
:author: あなたの名前

こんにちは！世界！
```

### ビルドする

操作は `data` ディレクトリの中で行います（biisan_data/dataの中）。

```
$ python -m biisan.generate
```

もし、以下のようなエラーが出た場合には、イニシャライズした際に表示された環境変数を設定していないためです。

```
Traceback (most recent call last):
（省略）
KeyError: 'BIISAN_SETTINGS_MODULE'
```

環境変数を設定していない場合には設定をし直して再度コマンドを実行してみましょう。

```
$ export BIISAN_SETTINGS_MODULE=biisan_local_settings
$ python -m biisan.generate
```

もし、以下のようなエラーが出た場合には、コマンドを実行しているフォルダが間違っています。 `biisan_data/data` の中で実行しましょう。

```
Traceback (most recent call last):
（省略）
ModuleNotFoundError: No module named 'biisan_local_settings'
```

うまくいくと次のように出力されますので、ブラウザで開いてみましょう。

```
$ python -m biisan.generate
BIISAN 0.3.0
INFO:__main__:Write:（省略）/biisan_data/out/blog/2019/05/05/my_first_biisan_entry/index.html
INFO:__main__:Write:（省略）/biisan_data/out/about/index.html
```

エントリーに記載した `date` と `slug` でURLが構成されます。この時点ではdataフォルダとoutフォルダは以下のようになります。

```
.
├── data
│   ├── __pycache__
│   │   └── biisan_local_settings.cpython-37.pyc
│   ├── biisan_local_settings.py
│   ├── blog
│   │   └── my_first_entry.rst
│   ├── extra
│   │   └── about.rst
│   └── templates
└── out
    ├── about
    │   └── index.html
    ├── api
    │   ├── feed
    │   │   └── index.xml
    │   └── google_sitemaps
    │       └── index.xml
    ├── blog
    │   ├── 2019
    │   │   └── 05
    │   │       ├── 05
    │   │       │   └── my_first_biisan_entry
    │   │       │       └── index.html
    │   │       └── index.html
    │   └── index.html
    └── index.html
```

ファイル名はindex.htmlですが、Webサーバーのディレクトリーインデックスの指定で省略できることを想定しています。

例えば `https://www.tsuyukimakoto.com/about/` のように、ファイル名を省略した場合にindex.htmlが返るように設定してください。

エントリーのパスはエントリーのrstファイルに記述した `slug` と `date` を元に作成されます。

```
:slug: my_first_biisan_entry
:date: 2019-05-05 13:00
```

## テンプレート

ディレクティブごとにテンプレートが用意されています。スタイルなどを変更したい場合にはテンプレートをtemplatesフォルダに置きます。

[デフォルトのテンプレート](https://github.com/tsuyukimakoto/biisan/tree/master/biisan/templates) と [実際のプロジェクトのテンプレート](https://github.com/tsuyukimakoto/tsuyukimakoto.com/tree/master/data/templates) がどうなっているか参照してみてください。

## デプロイ

outの中身を適切なサーバへ配備しましょう。ディレクトリーインデックスの指定を忘れずに。

## 追加のdocinfo

:slug: などと同様に、任意の（ただし、Storyクラスのアトリビュートと重複しないもの）docinfoを追加できます。

例えば、 **:og_image: https\://www.tsuyukimakoto.com/example.png** とした場合、テンプレート上で次のように使われることを想定しています。

{% if element.has_additional_meta("og_image") %}
let's output {{ element.og_image }}
{% endif %}

docinfoの区切り文字が : (コロン) であるため、:は **\\** でエスケープします。

