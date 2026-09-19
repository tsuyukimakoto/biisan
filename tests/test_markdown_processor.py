from biisan.markdown_processor import extract_yaml_frontmatter, parse_markdown_to_xml


def test_extracts_yaml_frontmatter() -> None:
    markdown = """---
title: Hello
published: 2026-09-19
tags:
  - python
---
# Heading
"""

    metadata, content = extract_yaml_frontmatter(markdown)

    assert metadata['title'] == 'Hello'
    assert str(metadata['published']) == '2026-09-19'
    assert metadata['tags'] == ['python']
    assert content == '# Heading\n'


def test_invalid_yaml_is_left_as_content() -> None:
    markdown = '---\ntitle: [\n---\n# Heading\n'

    metadata, content = extract_yaml_frontmatter(markdown)

    assert metadata == {}
    assert content == markdown


def test_converts_markdown_blocks_and_inline_elements() -> None:
    markdown = """---
title: Hello
slug: hello
date: 2026-09-19 10:00
author: Makoto
---
# Heading

Paragraph with **bold**, *emphasis*, `code`, [link](https://example.com), and ![alt](image.png).

> Quoted once.

1. first
2. second

| Name | Value |
| --- | --- |
| one | two |

---

```python
print('hello')
```

<span>raw</span>
"""

    document = parse_markdown_to_xml(markdown)

    assert document.tag == 'document'
    assert document.findtext('./docinfo/field/field_name') == 'title'
    assert document.findtext('./section/title') == 'Heading'
    assert document.findtext('.//strong') == 'bold'
    assert document.findtext('.//emphasis') == 'emphasis'
    assert document.findtext('.//literal') == 'code'
    assert document.find('.//reference').get('refuri') == 'https://example.com'
    assert document.find('.//image').get('alt') == 'alt'
    assert len(document.findall('.//block_quote/paragraph')) == 1
    assert len(document.findall('.//enumerated_list/list_item')) == 2
    assert document.find('.//table/tgroup').get('cols') == '2'
    assert document.find('.//transition') is not None
    assert document.find('.//literal_block').get('language') == 'python'
    assert document.find('.//raw').get('format') == 'html'
