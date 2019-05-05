# biisan

[![travis](https://travis-ci.org/tsuyukimakoto/biisan.svg?branch=master)](https://travis-ci.org/tsuyukimakoto/biisan) [![codecov](https://codecov.io/gh/tsuyukimakoto/biisan/branch/master/graph/badge.svg)](https://codecov.io/gh/tsuyukimakoto/biisan) [![Updates](https://pyup.io/repos/github/tsuyukimakoto/biisan/shield.svg)](https://pyup.io/repos/github/tsuyukimakoto/biisan/) [![Python 3](https://pyup.io/repos/github/tsuyukimakoto/biisan/python-3-shield.svg)](https://pyup.io/repos/github/tsuyukimakoto/biisan/)[![Reviewed by Hound](https://img.shields.io/badge/Reviewed_by-Hound-8E64B0.svg)](https://houndci.com)[![codebeat badge](https://codebeat.co/badges/e5a0ad5d-baab-4795-b07d-e03594b477d4)](https://codebeat.co/projects/github-com-tsuyukimakoto-biisan-master)

biisan is a static site generator that can write documents in [reStructuredText](http://docutils.sourceforge.net/rst.html).

## Feature

- Convert the structure of reStructuredText to the structure of object, and output to html with jinja2 template for each [Directives](http://docutils.sourceforge.net/docs/user/rst/cheatsheet.txt) of reStructuredText
- The default template is attached for the directives supported by biisan, but the template to be used can be replaced if the search destination is set in the configuration
- The conversion processor from directive to object can also replace any processor by setting
- The processing of the directive which is not supported is also possible by the same mechanism as replacement.
- Easy definition of new directives
- The process of converting the structure of reStructuredText to an object is performed in parallel in multiprocessing

## quick start

### Installation

It can be installed with pip. Since dependent libraries are also installed at the same time, you may want to create and install a virtual environment using venv if you want to be able to erase them cleanly.

```
$ pip install biisan
```

### Initialize

Generate the basic structure of biisan and configuration file. There is a folder called `biisan_data` under the folder you have run.

Answer `blog title`, `base URL`, `language code` as it is asked. You can change it later in the configuration file.

```
$ python -m biisan.main
? What's your blog title  blog title
? input your blog base url. like https://www.tsuyukimakoto.com  http:localhost
? input your blog language like ja  en

        Always set environment variable BIISAN_SETTINGS_MODULE to biisan_local_settings like bellow.

        $ export BIISAN_SETTINGS_MODULE=biisan_local_settings

```

Finally, the environment variables required whenever using biisan are output. It is an environment variable that is always required when using biisan.

It is a setting framework setting of [glueplate](https://pypi.org/project/glueplate/).

### First Entry

Let's check the contents of the generated folder.

```
$ cd biisan_data
$ tree
.
├── data
│   ├── biisan_local_settings.py
│   ├── blog
│   ├── extra
│   │   └── about.rst
│   └── templates
└── out
```

Inside the `biisan_data` folder there are two folders, `data` and `out`.

- data

    - biisan_local_settings.py

        setting file. It has been added to or overwritten in the [Original file settings](https://github.com/tsuyukimakoto/biisan/blob/master/biisan/biisan_settings.py) settings.

    - blog

        Put the reStructuredText file in this. It is good to make a folder so that it is easy to organize. The folder structure in the blog folder has nothing to do with the path of the output URL.

    - extra

        Put the file if you want to create a separate page from the date based entry. about is set by default.
        When newly added, add the definition of GLUE_PLATE_PLUS_BEFORE_extra to the setting file (data/biisan_local_settings.py).

        For example, if you put the file imusing.rst, define `GLUE_PLATE_PLUS_BEFORE_extra` in `data/biisan_local_settings.py` as follows.

        ```
        # Omitted

        settings = _(
            # 省略
            multiprocess = 8,
            GLUE_PLATE_PLUS_BEFORE_extra = [
                'imusing',
            ],
        )
        ```

        This is how glueplate works, ['imusing' before the `extra` setting in the [original file settings file](https://github.com/tsuyukimakoto/biisan/blob/master/biisan/biisan_settings.py) ',] Is added.

        See also [Actual setting](https://github.com/tsuyukimakoto/tsuyukimakoto.com/blob/master/data/biisan_local_settings.py#L19).

    - templates

        Put the template you want to overwrite. Like `GLUE_PLATE_PLUS_BEFORE_extra`, `GLUE_PLATE_PLUS_BEFORE_template_dirs` is defined in the configuration file, so first we will start looking for template files in this folder.

- out

      Html is output statically in this folder.

### This is the first entry

Let's save as `my_first_entry.rst` in `data/blog` as follows. The file name may be anything before the file extension, as long as the extension is .rst.

```
Is the first entry
=========================================================

:slug: my_first_biisan_entry
:date: 2019-05-05 13:00
:author: Your name

Hello! world!
```

### Build

The operation is done in the `data` directory (in biisan_data/data).

```
$ python -m biisan.generate
```

If you get an error like the following, it is because you have not set the environment variable displayed at the time of initialization.

```
Traceback (most recent call last):
(Omitted)
KeyError: 'BIISAN_SETTINGS_MODULE'
```

If you have not set the environment variable, try setting again and executing the command again.

```
$ export BIISAN_SETTINGS_MODULE=biisan_local_settings
$ python -m biisan.generate
```

If you get the following error, the folder where you are executing the command is wrong. Let's execute it in `biisan_data/data`.

```
Traceback (most recent call last):
(Omitted)
ModuleNotFoundError: No module named 'biisan_local_settings'
```

If it works, the output is as follows, so let's open it in a browser.

```
$ python -m biisan.generate
BIISAN 0.3.0
INFO:__main__:Write:(omitted)/biisan_data/out/blog/2019/05/05/my_first_biisan_entry/index.html
INFO:__main__:Write:(omitted)/biisan_data/out/about/index.html
```

The URL is composed of `date` and `slug` described in the entry. At this point, the data folder and the out folder are as follows.

```
.
├── data
│   ├── __pycache__
│   │   └── biisan_local_settings.cpython-37.pyc
│   ├── biisan_local_settings.py
│   ├── blog
│   │   └── my_first_entry.rst
│   ├── extra
│   │   └── about.rst
│   └── templates
└── out
    ├── about
    │   └── index.html
    ├── api
    │   ├── feed
    │   │   └── index.xml
    │   └── google_sitemaps
    │       └── index.xml
    ├── blog
    │   ├── 2019
    │   │   └── 05
    │   │       ├── 05
    │   │       │   └── my_first_biisan_entry
    │   │       │       └── index.html
    │   │       └── index.html
    │   └── index.html
    └── index.html
```

Although the file name is index.html, it is assumed that it can be omitted by specifying the directory index of the Web server.

For example, `https://www.tsuyukimakoto.com/about/` should be set to return index.html if the file name is omitted.

The entry path is created based on `slug` and `date` described in the entry rst file.

```
:slug: my_first_biisan_entry
:date: 2019-05-05 13:00
```

## template

A template is provided for each directive. Put templates in the templates folder if you want to change the style etc.

[Default template](https://github.com/tsuyukimakoto/biisan/tree/master/biisan/templates) and [real project template](https://github.com/tsuyukimakoto/tsuyukimakoto.com/tree/master/data/templates).

## Deploy

Deploy the contents of out to an appropriate server. Don't forget to specify the directory index.
