# biisan

biisan is a static site generator for blogs written in reStructuredText or Markdown. It converts documents into model objects and renders them with replaceable Jinja templates.

[日本語](README.ja.md)

## Requirements

- Python 3.11 or later

## Features

- Write entries in reStructuredText or GitHub Flavored Markdown
- Render pages with replaceable Jinja templates
- Generate the blog index, monthly archives, a complete entry list, RSS feeds, and a sitemap
- Generate a separate RSS feed for every entry category
- Add custom metadata to entries and use it from templates
- Register custom Jinja filters and global functions
- Parse entries in parallel and avoid rewriting unchanged pages with a SHA-256 render cache

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
:category: notes

Hello, world!
```

Markdown entries use YAML front matter:

```markdown
---
slug: my-markdown-entry
date: 2026-09-19 14:00
author: Your name
category: notes
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

Entry URLs are derived from each entry's `date` and `slug`.

Markdown supports headings, paragraphs, emphasis, links, images, lists, block quotes, fenced code blocks, tables, thematic breaks, and inline or block HTML. Raw HTML is copied to the generated page, so use Markdown input from trusted authors.

## Generated files

A build writes these pages under `biisan_data/out/`:

| Path | Contents |
| --- | --- |
| `/index.html` | Site top page |
| `/blog/index.html` | Recent entries and archive links |
| `/blog/all/index.html` | All entries |
| `/blog/YYYY/MM/index.html` | Monthly archive |
| `/blog/YYYY/MM/DD/slug/index.html` | Entry page |
| `/api/feed/index.xml` | RSS feed for recent entries |
| `/api/feed/category/index.xml` | RSS feed for a category |
| `/api/google_sitemaps/index.xml` | Sitemap |
| `/name/index.html` | Extra page such as `about.rst` |

An entry with `category: notes` produces `/api/feed/notes/index.xml`. The number of entries included in each RSS feed is controlled by `latest_list_count`.

Each rendered entry and extra page also has a `.biisan.raw.sha256` file. On the next build, biisan skips minification and writing when the rendered content has not changed.

## Customize

Edit `biisan_local_settings.py` to change the site configuration. Common settings are:

| Setting | Purpose |
| --- | --- |
| `blog.title` | Site title |
| `blog.base_url` | Absolute base URL used by feeds and the sitemap |
| `blog.language` | RSS language code |
| `dir.output` | Output directory |
| `timezone` | Time zone assigned to entry dates |
| `latest_list_count` | Number of recent entries in lists and feeds |
| `multiprocess` | Number of document parser processes |
| `extra` | Names of additional `.rst` pages in `data/extra/` |
| `custom_filters` | Jinja filter name-to-callable mapping |
| `template_functions` | Jinja global name-to-callable mapping |

Put templates with the same relative path as the bundled templates in `data/templates/` to override them. The generated settings file adds that directory before the built-in template directory.

Additional reStructuredText docinfo or Markdown front-matter fields are available to templates as attributes of the story object, provided their names do not conflict with built-in attributes.

For example, `category` is available as `element.category` in an entry template. Test optional metadata before reading it:

```jinja2
{% if element.has_additional_meta("og_image") %}
  <meta property="og:image" content="{{ element.og_image }}">
{% endif %}
```

## Development

The repository uses [uv](https://docs.astral.sh/uv/). Dependency resolution excludes distributions uploaded within the last seven days.

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
