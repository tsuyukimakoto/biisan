# biisan

[![travis](https://travis-ci.org/tsuyukimakoto/biisan.svg?branch=master)](https://travis-ci.org/tsuyukimakoto/biisan) [![codecov](https://codecov.io/gh/tsuyukimakoto/biisan/branch/master/graph/badge.svg)](https://codecov.io/gh/tsuyukimakoto/biisan) [![Updates](https://pyup.io/repos/github/tsuyukimakoto/biisan/shield.svg)](https://pyup.io/repos/github/tsuyukimakoto/biisan/) [![Python 3](https://pyup.io/repos/github/tsuyukimakoto/biisan/python-3-shield.svg)](https://pyup.io/repos/github/tsuyukimakoto/biisan/)[![Reviewed by Hound](https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg)](https://houndci.com)[![codebeat badge](https://codebeat.co/badges/e5a0ad5d-baab-4795-b07d-e03594b477d4)](https://codebeat.co/projects/github-com-tsuyukimakoto-biisan-master)

biisan（ビーサン）は、[reStructuredText](http://docutils.sourceforge.net/rst.html)で文書を記述できるスタティックサイトジェネレーターです。

## 特徴

- reStructuredTextの構造をオブジェクトの構造に変換し、reStructuredTextの[ディレクティブ](http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt)ごとにjinja2のテンプレートでhtmlに出力します
- biisanで対応しているディレクティブに関してはデフォルトのテンプレートが付属しますが、設定で探索先を設定すると利用するテンプレートを差し替えられます
- ディレクティブからオブジェクトへの変換プロセッサーも設定で任意のプロセッサーを差し替えられます
- 対応していないディレクティブの処理も差し替えと同様の仕組みで対応可能です
- 新しいディレクティブの定義も容易です
- reStructuredTextの構造をオブジェクトへ変換する処理はmultiprocessingで並行して行われます

