from FleaHive import clean


def test_clean_removes_frontmatter_at_start():
    text = """---
title: Sample
tags: [test]
---

Body content starts here.
"""
    assert clean(text) == "Body content starts here."


def test_clean_keeps_content_after_mid_body_rule():
    text = """Introduction paragraph.

---

Content should remain after the rule.
"""
    cleaned = clean(text)
    assert "Content should remain after the rule." in cleaned
    assert "---" in cleaned


def test_clean_strips_markdown_and_links():
    text = """# Heading

Here is a [link](https://example.com) with **bold** text,
an image ![alt](image.png), and a citation https://arxiv.org/1234.
"""
    cleaned = clean(text)
    assert "[" not in cleaned and "]" not in cleaned
    assert "https://" not in cleaned
    assert "image.png" not in cleaned
    assert "Heading" in cleaned and "bold" in cleaned
