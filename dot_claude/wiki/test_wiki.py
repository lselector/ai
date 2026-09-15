#!/usr/bin/env python3
"""Unit tests for the project wiki tools.

Covers frontmatter parsing, link extraction, init,
index, log, check, and (when flask is installed) the
web server routes. Each test builds a wiki in a
temporary folder.

Usage:
    python3 ~/.claude/wiki/test_wiki.py
    ~/.venvs/standard/bin/python ~/.claude/wiki/test_wiki.py

Created: 2026-09-15
Last updated: 2026-09-15
"""

import importlib
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wiki_edit as we  # noqa: E402
import wiki_pages as wp  # noqa: E402

CONCEPT = """---
type: Concept
title: "Envelope Encryption"
description: Encrypt data keys with a master key.
tags: [security, keys]
---

# Envelope Encryption

Uses [[AWS KMS]] and [[Missing Page|a missing page]].
"""

ENTITY = """---
type: Entity
tags:
  - vendor
  - aws
---

# AWS KMS

Backs [[Envelope Encryption]].
"""


# --------------------------------------------------------------
def make_wiki(tmp):
    """Create a small wiki with two linked pages."""
    root = Path(tmp) / "proj" / "wiki"
    we.init(root)
    (root / "Wiki/Concepts/Envelope Encryption.md") \
        .write_text(CONCEPT, encoding="utf-8")
    (root / "Wiki/Entities/AWS KMS.md") \
        .write_text(ENTITY, encoding="utf-8")
    return root


# --------------------------------------------------------------
class TestParsing(unittest.TestCase):
    """Frontmatter and link parsing."""

    # --------------------------------------
    def test_flow_and_block_lists(self):
        """Both YAML list styles become Python lists."""
        meta, body = wp.split_frontmatter(CONCEPT)
        self.assertEqual(meta["title"], "Envelope Encryption")
        self.assertEqual(meta["tags"], ["security", "keys"])
        self.assertTrue(body.lstrip().startswith("# Env"))
        meta, _ = wp.split_frontmatter(ENTITY)
        self.assertEqual(meta["tags"], ["vendor", "aws"])

    # --------------------------------------
    def test_no_frontmatter(self):
        """Text without frontmatter is all body."""
        self.assertEqual(wp.split_frontmatter("# X"),
                         ({}, "# X"))

    # --------------------------------------
    def test_links(self):
        """Aliases, anchors and paths reduce to names."""
        text = "[[A]] [[B|bee]] [[C#part]] [[x/D]]"
        self.assertEqual(wp.links(text),
                         ["A", "B", "C", "D"])


# --------------------------------------------------------------
class TestEdit(unittest.TestCase):
    """init, index, log and check on a temp wiki."""

    # --------------------------------------
    def setUp(self):
        """Fresh temp wiki per test."""
        self.tmp = tempfile.TemporaryDirectory()
        self.root = make_wiki(self.tmp.name)

    # --------------------------------------
    def tearDown(self):
        """Remove the temp wiki."""
        self.tmp.cleanup()

    # --------------------------------------
    def test_init_idempotent(self):
        """Second init creates nothing, keeps edits."""
        topics = self.root / "Dashboards/Topics.md"
        topics.write_text("---\ntype: Dashboard\n---\nmine")
        self.assertEqual(we.init(self.root), [])
        self.assertTrue(topics.read_text().endswith("mine"))

    # --------------------------------------
    def test_index_lists_pages(self):
        """Index links every page with its description."""
        text = we.build_index(self.root).read_text()
        self.assertIn("[[Envelope Encryption]] - Encrypt",
                      text)
        self.assertIn("## Entities (1)", text)

    # --------------------------------------
    def test_log_groups_by_day(self):
        """Same day appends; new day adds a heading."""
        we.append_log(self.root, "one", today="2030-01-01")
        we.append_log(self.root, "two", today="2030-01-01")
        we.append_log(self.root, "three", today="2030-01-02")
        text = (self.root / "Dashboards/Log.md").read_text()
        self.assertEqual(text.count("## 2030-01-01"), 1)
        self.assertTrue(text.endswith(
            "## 2030-01-02\n\n- three\n"))

    # --------------------------------------
    def test_check(self):
        """Reports missing type, dangling link, index."""
        (self.root / "Wiki/Concepts/Bad.md").write_text("x")
        errors, warnings = wp.check(self.root)
        self.assertTrue(any("Bad.md: no 'type'" in e
                            for e in errors))
        self.assertTrue(any("[[Missing Page]]" in w
                            for w in warnings))
        self.assertTrue(any("not in Index" in w
                            for w in warnings))
        (self.root / "Wiki/Concepts/Bad.md").unlink()
        we.build_index(self.root)
        errors, warnings = wp.check(self.root)
        self.assertEqual(errors, [])
        self.assertFalse(any("not in Index" in w
                             for w in warnings))

    # --------------------------------------
    def test_backlinks_and_root_search(self):
        """Backlinks work; root is found from a subdir."""
        names = [p.name for p in
                 wp.backlinks("AWS KMS", self.root)]
        self.assertIn("Envelope Encryption", names)
        sub = self.root.parent / "src" / "pkg"
        sub.mkdir(parents=True)
        old = os.getcwd()
        try:
            os.chdir(sub)
            os.environ.pop("WIKI_ROOT", None)
            self.assertEqual(wp.get_root(),
                             self.root.resolve())
        finally:
            os.chdir(old)


# --------------------------------------------------------------
@unittest.skipUnless(importlib.util.find_spec("flask"),
                     "flask not installed")
class TestServer(unittest.TestCase):
    """Server routes via the flask test client."""

    # --------------------------------------
    def test_routes(self):
        """Page, search, raw traversal and 404."""
        with tempfile.TemporaryDirectory() as tmp:
            root = make_wiki(tmp)
            we.build_index(root)
            sys.argv = ["wiki_server.py", str(root)]
            server = importlib.import_module("wiki_server")
            c = server.app.test_client()
            self.assertEqual(c.get("/").status_code, 302)
            page = c.get("/wiki/Envelope Encryption").text
            self.assertIn('href="/wiki/AWS%20KMS"', page)
            self.assertIn('class="missing"', page)
            self.assertIn("What links here", page)
            hits = c.get("/search?q=kms").text
            self.assertIn("3 pages found", hits)
            bad = c.get("/raw/../Dashboards/Log.md")
            self.assertEqual(bad.status_code, 404)
            self.assertEqual(c.get("/raw/sources.md")
                             .status_code, 200)
            self.assertEqual(c.get("/styles.css")
                             .status_code, 200)


# --------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
