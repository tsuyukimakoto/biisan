from pathlib import Path

import pytest

from biisan.main import (
    initialize_structures,
)

from ._constants import (
    ANSWER,
    DATA_DIR,
)
from ._utils import (  # noqa
    cd,
    cleanup,
    copy_first_blog,
    copy_second_blog,
    copy_test_local_settings,
    setenv,
)


def test_register_processor():
    with cd("tests"):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()

        # need data structure before import biisan.generate
        from glueplate import config

        from biisan.generate import register_processor

        register_processor()

        import biisan.generate

        assert biisan.generate.processor_registry is not None
        assert [
            "biisan.processors." + processor for processor in list(biisan.generate.processor_registry.keys())
        ] == config.settings.processors


def test_processors():
    with cd("tests"):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()
        copy_first_blog()
        copy_second_blog()

        with cd("biisan_data/data"):
            from biisan.generate import main, prepare

            prepare()
            main()


def test_marshal():
    with cd("tests"):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()
        copy_first_blog()
        copy_second_blog()

        with cd("biisan_data/data"):
            from biisan.generate import glob_rst_documents, prepare

            prepare()
            story_list = glob_rst_documents("./blog")
            first_story = story_list[0]
            second_story = story_list[1]
            assert str(first_story.title) == "My First Blog"
            assert str(first_story.url) == "/blog/2019/04/06/my_first_blog/"
            assert str(first_story.author) == "makoto tsuyuki"
            assert str(second_story.title) == "My Second Blog"
            assert str(second_story.url) == "/blog/2019/04/15/my_second_blog/"
            assert not first_story.has_additional_meta("other_url")
            assert second_story.has_additional_meta("other_url")
            assert second_story.other_url == "https://www.tsuyukimakoto.com/"


def test_unmarshal():
    with cd("tests"):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()
        copy_first_blog()
        copy_second_blog()

        with cd("biisan_data/data"):
            from biisan.generate import output, unmarshal_story

            story_list = unmarshal_story((Path(".") / "blog" / "my_first_blog.rst").absolute())
            output([story_list])
            Path("")
        output_data = "output"
        with cd("biisan_data/out"):
            output_file = Path(".") / "blog" / "2019" / "04" / "06" / "my_first_blog" / "index.html"
            assert output_file.exists()

            with open(output_file) as f:
                output_data = f.read()

        assert "<title>My First Blog</title>" in output_data
        assert "<h2>This is my first Blog</h2>" in output_data
        assert "<strong>paragraph!</strong>" in output_data
        assert "href=http://localhost/api/feed/index.xml" in output_data


def test_unmarshal_markdown():
    markdown = """---
title: Markdown Entry
slug: markdown-entry
date: 2026-09-19 10:00
author: Makoto
category: notes
---
# Markdown Entry

Paragraph with **bold** and [a link](https://example.com).
"""
    with cd("tests"):
        initialize_structures(DATA_DIR, ANSWER)
        copy_test_local_settings()
        markdown_path = Path("biisan_data/data/blog/markdown-entry.md")
        markdown_path.write_text(markdown, encoding="utf8")

        with cd("biisan_data/data"):
            from biisan.generate import unmarshal_story

            story = unmarshal_story(Path("blog/markdown-entry.md"))

    assert str(story.title) == "Markdown Entry"
    assert story.slug == "markdown-entry"
    assert story.author == "Makoto"
    assert story.category == "notes"
    story.prepare_html([story], 0)
    assert "<strong>bold</strong>" in story.to_html()


def test_write_html_uses_digest_cache(tmp_path):
    from biisan.generate import write_html

    class StoryStub:
        directory = str(tmp_path)
        rendered = "<html><body><p>First</p></body></html>"

        def to_html(self):
            return self.rendered

    story = StoryStub()

    assert write_html(story) is True
    assert write_html(story) is False

    story.rendered = "<html><body><p>Second</p></body></html>"
    assert write_html(story) is True
    assert (tmp_path / ".biisan.raw.sha256").exists()


def test_unmarshal_rejects_unknown_extension(tmp_path):
    from biisan.generate import unmarshal_story

    path = tmp_path / "entry.txt"
    path.write_text("unsupported", encoding="utf8")

    with pytest.raises(ValueError, match="Only .rst and .md are supported"):
        unmarshal_story(path)
