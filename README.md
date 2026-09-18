# biisan

biisan is a static site generator for blogs written in reStructuredText or Markdown. It converts documents into model objects and renders them with replaceable Jinja templates.

[日本語](README.ja.md)

## Requirements

- Python 3.11 or later

## Install

Create a virtual environment and install biisan from PyPI:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install biisan
```

## Create a site

Run the initializer in the directory where you want the site project:

```console
python -m biisan.main
```

It creates this structure:

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

Add a reStructuredText entry to `biisan_data/data/blog/`:

```rst
My first entry
==============

:slug: my-first-entry
:date: 2026-09-19 13:00
:author: Your name

Hello, world!
```

Markdown entries use YAML front matter:

```markdown
---
slug: my-markdown-entry
date: 2026-09-19 14:00
author: Your name
---

# My Markdown entry

Hello, Markdown!
```

Generate the site from the data directory:

```console
cd biisan_data/data
export BIISAN_SETTINGS_MODULE=biisan_local_settings
python -m biisan.generate
```

Generated HTML, RSS feeds, and the sitemap are written under `biisan_data/out/`. Entry URLs are derived from each entry's `date` and `slug`.

## Customize

Edit `biisan_local_settings.py` to change the title, base URL, language, output directory, multiprocessing count, processors, and directives. Put templates with the same relative path as the bundled templates in `data/templates/` to override them.

Additional reStructuredText docinfo or Markdown front-matter fields are available to templates as attributes of the story object, provided their names do not conflict with built-in attributes.

## Development

The repository uses [uv](https://docs.astral.sh/uv/):

```console
uv sync --locked
uv run pytest
uv run ruff format --check src tests
uv run ruff check src tests
uv run pyrefly check
uv build
uv run twine check dist/*
```

The test suite is run on Python 3.11 through 3.14.

## License

MIT
