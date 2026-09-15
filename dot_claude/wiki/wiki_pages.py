#!/usr/bin/env python3
"""Read-only page model for a project wiki (OKF Markdown).

Stdlib-only core shared by wiki_tools.py (CLI) and
wiki_server.py (web UI). It knows the wiki layout,
parses OKF frontmatter, extracts [[wiki links]], and
answers find / grep / read / backlinks / check queries.
It never writes files; wiki_edit.py does that.

Layout of a wiki root (normally <repo>/wiki):
    Inbox/  Raw/  Dashboards/
    Wiki/Concepts/  Wiki/Entities/  Wiki/Summaries/

Usage:
    import wiki_pages as wp
    root = wp.get_root()          # $WIKI_ROOT or ./wiki
    idx = wp.page_index(root)     # name -> Page
    meta, body = wp.split_frontmatter(text)
    wp.links(body)                # ['Page A', ...]
    wp.grep("rate limit", root)   # 'path:line: text'
    errors, warnings = wp.check(root)

Created: 2026-09-15
Last updated: 2026-09-15
"""

import fnmatch
import os
import re
from dataclasses import dataclass
from pathlib import Path

SECTIONS = {
    "Concepts": "Wiki/Concepts",
    "Entities": "Wiki/Entities",
    "Summaries": "Wiki/Summaries",
    "Dashboards": "Dashboards",
}
LAYOUT = ["Inbox", "Raw", *SECTIONS.values()]
RESERVED = {"index.md", "log.md"}
SOURCES_FILE = "sources.md"

LINK_RX = re.compile(
    r"\[\[([^\]|\n]+?)(?:\|([^\]\n]+))?\]\]"
)
FM_RX = re.compile(
    r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S
)
PAIR_RX = re.compile(r"^([A-Za-z_][\w-]*):\s*(.*?)\s*$")
ITEM_RX = re.compile(r"^\s*-\s+(.*?)\s*$")


# --------------------------------------------------------------
@dataclass(frozen=True)
class Page:
    """One wiki page: its name, section and file."""

    name: str
    section: str
    path: Path

    # --------------------------------------
    def text(self):
        """Return the page source text."""
        return self.path.read_text(
            encoding="utf-8", errors="replace"
        )


# --------------------------------------------------------------
def get_root(root=None):
    """Resolve the wiki root: arg, $WIKI_ROOT, or search."""
    root = root or os.environ.get("WIKI_ROOT")
    if root:
        return Path(root).expanduser().resolve()
    here = Path.cwd().resolve()
    for folder in [here, *here.parents]:
        if (folder / "wiki").is_dir():
            return folder / "wiki"
        if (folder / ".git").exists():
            return folder / "wiki"
    return here / "wiki"


# --------------------------------------------------------------
def project_name(root):
    """Name of the project that owns the wiki."""
    return Path(root).resolve().parent.name


# --------------------------------------------------------------
def pages(root):
    """List every page in the wiki sections, in order."""
    out = []
    for sec, rel in SECTIONS.items():
        folder = Path(root) / rel
        if folder.is_dir():
            out += [Page(p.stem, sec, p)
                    for p in sorted(folder.glob("*.md"))]
    return out


# --------------------------------------------------------------
def page_index(root):
    """Map page name -> Page; the first name wins."""
    idx = {}
    for page in pages(root):
        idx.setdefault(page.name, page)
    return idx


# --------------------------------------------------------------
def unquote_value(value):
    """Strip one pair of matching surrounding quotes."""
    if len(value) >= 2 and value[0] == value[-1] \
            and value[0] in "'\"":
        return value[1:-1]
    return value


# --------------------------------------------------------------
def scalar(value):
    """Parse a YAML scalar or a [a, b] flow list."""
    if value.startswith("[") and value.endswith("]"):
        items = [unquote_value(v.strip())
                 for v in value[1:-1].split(",")]
        return [v for v in items if v]
    return unquote_value(value)


# --------------------------------------------------------------
def parse_meta(block):
    """Parse flat YAML: scalars and lists, one key a line."""
    meta, last = {}, None
    for line in block.splitlines():
        item = ITEM_RX.match(line)
        if item and last is not None:
            if not isinstance(meta[last], list):
                meta[last] = []
            meta[last].append(unquote_value(item.group(1)))
            continue
        pair = PAIR_RX.match(line)
        if pair:
            last = pair.group(1)
            meta[last] = scalar(pair.group(2))
    return meta


# --------------------------------------------------------------
def split_frontmatter(text):
    """Return (meta dict, body); meta is {} if absent."""
    m = FM_RX.match(text)
    if not m:
        return {}, text
    return parse_meta(m.group(1)), text[m.end():]


# --------------------------------------------------------------
def link_target(raw):
    """Page name a [[link]] points at."""
    return raw.split("#")[0].split("/")[-1].strip()


# --------------------------------------------------------------
def links(text):
    """Return the page names of all [[links]] in text."""
    return [link_target(m.group(1))
            for m in LINK_RX.finditer(text)]


# --------------------------------------------------------------
def docs(root):
    """All .md files under the wiki root, sorted."""
    return sorted(Path(root).rglob("*.md"))


# --------------------------------------------------------------
def rel(path, root):
    """Path relative to the wiki root, as posix text."""
    return Path(path).relative_to(root).as_posix()


# --------------------------------------------------------------
def find(pattern, root):
    """Relative .md paths matching a glob (path or name)."""
    out = []
    for p in docs(root):
        r = rel(p, root)
        if fnmatch.fnmatch(r, pattern) \
                or fnmatch.fnmatch(p.name, pattern):
            out.append(r)
    return out


# --------------------------------------------------------------
def grep(query, root, regex=False):
    """Case-insensitive 'path:line: text' hits."""
    rx = re.compile(query if regex else re.escape(query),
                    re.IGNORECASE)
    hits = []
    for p in docs(root):
        text = p.read_text(encoding="utf-8",
                           errors="replace")
        for n, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                hits.append(f"{rel(p, root)}:{n}: "
                            f"{line.strip()}")
    return hits


# --------------------------------------------------------------
def read(path, root):
    """Read one document by path relative to the root."""
    base = Path(root).resolve()
    doc = (base / path).resolve()
    if not doc.is_relative_to(base):
        raise ValueError(f"Path escapes wiki root: {path}")
    return doc.read_text(encoding="utf-8")


# --------------------------------------------------------------
def backlinks(name, root):
    """Pages that contain a [[link]] to the named page."""
    return [p for p in pages(root)
            if p.name != name and name in links(p.text())]


# --------------------------------------------------------------
def raw_files(root):
    """Source files in Raw/, except the registry."""
    folder = Path(root) / "Raw"
    if not folder.is_dir():
        return []
    return sorted(
        p for p in folder.rglob("*")
        if p.is_file() and p.name != SOURCES_FILE
        and not p.name.startswith(".")
    )


# --------------------------------------------------------------
def check_pages(root, idx):
    """Errors: missing type, duplicate names, bad links."""
    errors, warnings, seen = [], [], {}
    for page in pages(root):
        r = rel(page.path, root)
        if page.name in seen:
            errors.append(f"duplicate page name "
                          f"'{page.name}': {seen[page.name]}"
                          f" and {r}")
        seen.setdefault(page.name, r)
        meta, body = split_frontmatter(page.text())
        reserved = page.path.name.lower() in RESERVED
        if not reserved and not meta.get("type"):
            errors.append(f"{r}: no 'type' in frontmatter")
        for target in links(body):
            if target not in idx:
                warnings.append(
                    f"{r}: dangling link [[{target}]]")
    return errors, warnings


# --------------------------------------------------------------
def check_graph(root, idx):
    """Warnings: orphans and pages missing from Index."""
    inbound, warnings = set(), []
    for page in pages(root):
        if page.path.name.lower() != "index.md":
            inbound |= set(links(page.text())) - {page.name}
    index = idx.get("Index")
    listed = set(links(index.text())) if index else set()
    for page in pages(root):
        if page.section == "Dashboards":
            continue
        r = rel(page.path, root)
        if page.name not in inbound:
            warnings.append(f"{r}: orphan, no page links"
                            " to it")
        if page.name not in listed:
            warnings.append(f"{r}: not in Index; run index")
    return warnings


# --------------------------------------------------------------
def check_sources(root):
    """Warnings: unsummarised Raw files, Inbox backlog."""
    summarised = set()
    for page in pages(root):
        meta, _ = split_frontmatter(page.text())
        if meta.get("source_file"):
            summarised.add(str(meta["source_file"]))
    warnings = [
        f"{rel(p, root)}: no summary cites it "
        "(source_file)"
        for p in raw_files(root)
        if rel(p, root) not in summarised
    ]
    inbox = Path(root) / "Inbox"
    waiting = [p for p in inbox.glob("*")
               if not p.name.startswith(".")] \
        if inbox.is_dir() else []
    if waiting:
        warnings.append(f"Inbox/: {len(waiting)} item(s)"
                        " waiting to be filed")
    return warnings


# --------------------------------------------------------------
def check(root):
    """Lint the whole wiki; return (errors, warnings)."""
    idx = page_index(root)
    missing = [d for d in LAYOUT
               if not (Path(root) / d).is_dir()]
    errors = [f"missing folder {d}/" for d in missing]
    page_errors, warnings = check_pages(root, idx)
    warnings += check_graph(root, idx)
    warnings += check_sources(root)
    return errors + page_errors, warnings
