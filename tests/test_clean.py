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
