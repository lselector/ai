#!/usr/bin/env python3
"""Serve a project wiki as a local, Wikipedia-style website.

Read-only web UI over <repo>/wiki: [[wiki links]],
section listings, an infobox built from OKF frontmatter,
"what links here" backlinks, browsable Raw/ sources and
full-text search. Pages are re-read on every request,
so edits show up on refresh.

"/" shows Dashboards/Home.md when it exists, otherwise
the generated Dashboards/Index.md.

Usage:
    python wiki_server.py [wiki_dir]    # default: search
    PORT=8021 python wiki_server.py     # default 8020
    # background control scripts, same folder:
    server_start.sh [wiki_dir] / server_stop.sh
    server_restart.sh

Requires: flask, markdown. Styles: styles.css.

Created: 2026-09-15
Last updated: 2026-09-15
"""

import html
import os
import re
import sys
from pathlib import Path
from urllib.parse import quote, unquote

import markdown as md
from flask import Flask, abort, redirect, request
from flask import send_file

import wiki_pages as wp

HERE = Path(__file__).resolve().parent
ROOT = wp.get_root(sys.argv[1] if len(sys.argv) > 1
                   else None)
RAW = ROOT / "Raw"
PORT = int(os.environ.get("PORT", "8020"))
TITLE = f"{wp.project_name(ROOT)} wiki"
PINNED = ["Home", "Index", "Topics", "Log"]
MD_EXTS = ["tables", "fenced_code", "sane_lists"]
INFOBOX_SKIP = {"title"}
HREF_RX = re.compile(
    r'href="(?!https?:|mailto:|/)([^"#]+?\.md)(#[^"]*)?"'
)

app = Flask(__name__)


# --------------------------------------------------------------
def page_url(name):
    """URL of a wiki page."""
    return "/wiki/" + quote(name)


# --------------------------------------------------------------
def anchor(url, label, cls=""):
    """HTML link with an escaped label."""
    c = f' class="{cls}"' if cls else ""
    return (f'<a{c} href="{html.escape(url, True)}">'
            f"{html.escape(label)}</a>")


# --------------------------------------------------------------
def wikify(text, idx):
    """Turn [[Name]] and [[Name|label]] into anchors."""

    # --------------------------------------
    def repl(m):
        target = wp.link_target(m.group(1))
        label = (m.group(2) or m.group(1)).strip()
        if target in idx:
            return anchor(page_url(target), label)
        return (f'<span class="missing">'
                f"{html.escape(label)}</span>")

    return wp.LINK_RX.sub(repl, text)


# --------------------------------------------------------------
def local_hrefs(body_html, idx):
    """Point plain Markdown links to .md files at pages."""

    # --------------------------------------
    def repl(m):
        stem = Path(unquote(m.group(1))).stem
        if stem in idx:
            return f'href="{page_url(stem)}"'
        return m.group(0)

    return HREF_RX.sub(repl, body_html)


# --------------------------------------------------------------
def render(body, idx):
    """Markdown body with wiki links -> HTML."""
    out = md.markdown(wikify(body, idx), extensions=MD_EXTS)
    return local_hrefs(out, idx)


# --------------------------------------------------------------
def sidebar(idx):
    """Navigation: pinned dashboards, sections, Raw."""
    items = [f"<li>{anchor(page_url(n), n)}</li>"
             for n in PINNED if n in idx]
    items.append("<hr>")
    counts = {}
    for page in idx.values():
        counts[page.section] = counts.get(page.section, 0) + 1
    for sec in wp.SECTIONS:
        link = anchor("/section/" + quote(sec), sec)
        items.append(f"<li>{link} ({counts.get(sec, 0)})"
                     "</li>")
    n_raw = len(wp.raw_files(ROOT))
    items.append(f'<li>{anchor("/raw/", "Raw sources")}'
                 f" ({n_raw})</li>")
    return ("<nav><h3>Navigation</h3><ul>"
            + "".join(items) + "</ul></nav>")


# --------------------------------------------------------------
def shell(title, body, idx, q=""):
    """Wrap content in the site layout."""
    safe_q = html.escape(q, quote=True)
    top = (
        '<header id="topbar">'
        f'<h1>{anchor("/", TITLE)}</h1>'
        '<form action="/search" method="get">'
        f'<input type="search" name="q" value="{safe_q}"'
        ' placeholder="Search the wiki..."'
        ' aria-label="Search the wiki"></form></header>'
    )
    return (
        '<!doctype html><html lang="en"><head>'
        '<meta charset="utf-8">'
        f"<title>{html.escape(title)}</title>"
        '<link rel="stylesheet" href="/styles.css">'
        "</head><body>" + top
        + '<div class="layout">' + sidebar(idx)
        + f"<main>{body}</main></div></body></html>"
    )


# --------------------------------------------------------------
def infobox_value(key, val):
    """Render one frontmatter value as HTML."""
    if isinstance(val, list):
        return html.escape(", ".join(map(str, val)))
    val = str(val)
    if re.match(r"https?://", val):
        return (f'<a class="ext" href="{html.escape(val, 1)}"'
                ' target="_blank" rel="noopener noreferrer">'
                f"{html.escape(val)}</a>")
    if key == "source_file" and val.startswith("Raw/"):
        return anchor("/raw/" + quote(val[4:]), val)
    return html.escape(val)


# --------------------------------------------------------------
def infobox(meta):
    """OKF frontmatter as a floating table."""
    rows = [
        f"<tr><th>{html.escape(str(k))}</th>"
        f"<td>{infobox_value(k, v)}</td></tr>"
        for k, v in meta.items()
        if v and k not in INFOBOX_SKIP
    ]
    if not rows:
        return ""
    return '<table class="infobox">' + "".join(rows) \
        + "</table>"


# --------------------------------------------------------------
def backlinks_html(name):
    """'What links here' footer."""
    hits = [anchor(page_url(p.name), p.name)
            for p in wp.backlinks(name, ROOT)]
    if not hits:
        return ""
    return ('<div class="backlinks"><b>What links here:'
            "</b> " + " &middot; ".join(hits) + "</div>")


# --------------------------------------------------------------
@app.route("/styles.css")
def styles():
    """The single stylesheet."""
    return send_file(HERE / "styles.css",
                     mimetype="text/css")


# --------------------------------------------------------------
@app.route("/")
def home():
    """Front page: Home if present, else Index."""
    idx = wp.page_index(ROOT)
    name = "Home" if "Home" in idx else "Index"
    return redirect(page_url(name))


# --------------------------------------------------------------
@app.route("/wiki/<name>")
def wiki_page(name):
    """One page by name."""
    idx = wp.page_index(ROOT)
    if name not in idx:
        abort(404)
    page = idx[name]
    meta, body = wp.split_frontmatter(page.text())
    ptype = html.escape(str(meta.get("type", page.section)))
    src = html.escape(wp.rel(page.path, ROOT))
    title = html.escape(str(meta.get("title", name)))
    if body.lstrip().startswith("# "):
        title = ""  # the body brings its own heading
    article = (
        (f"<h1>{title}</h1>" if title else "")
        + f'<div class="pagetype">{ptype} &middot; '
        f"<code>{src}</code></div>"
        + infobox(meta) + render(body, idx)
        + '<div class="clear"></div>'
        + backlinks_html(name)
    )
    return shell(name, article, idx)


# --------------------------------------------------------------
@app.route("/section/<sec>")
def section_page(sec):
    """List the pages of one section."""
    if sec not in wp.SECTIONS:
        abort(404)
    idx = wp.page_index(ROOT)
    items = []
    for page in wp.pages(ROOT):
        if page.section != sec:
            continue
        meta, _ = wp.split_frontmatter(page.text())
        desc = html.escape(str(meta.get("description", "")))
        link = anchor(page_url(page.name), page.name)
        items.append(f"<li>{link}"
                     + (f" - {desc}" if desc else "")
                     + "</li>")
    body = (f"<h1>{html.escape(sec)}</h1>"
            f"<p>{len(items)} pages</p><ul>"
            + "".join(items) + "</ul>")
    return shell(sec, body, idx)


# --------------------------------------------------------------
@app.route("/raw/")
def raw_index():
    """All immutable sources, grouped by folder."""
    idx = wp.page_index(ROOT)
    groups = {}
    for p in wp.raw_files(ROOT):
        folder = p.parent.relative_to(RAW).as_posix()
        groups.setdefault(folder, []).append(p)
    out = ["<h1>Raw sources</h1><p>Immutable source files."
           " Wiki pages are derived from these.</p>"]
    if (RAW / wp.SOURCES_FILE).is_file():
        link = anchor("/raw/" + wp.SOURCES_FILE,
                      "Source registry")
        out.append(f"<p>{link}</p>")
    for folder, files in sorted(groups.items()):
        label = "Raw/" if folder == "." else folder
        out.append(f"<h2>{html.escape(label)} "
                   f"({len(files)})</h2><ul>")
        for f in files:
            url = "/raw/" + quote(wp.rel(f, RAW))
            out.append(f"<li>{anchor(url, f.name)}</li>")
        out.append("</ul>")
    return shell("Raw sources", "".join(out), idx)


# --------------------------------------------------------------
def resolve_raw(rel):
    """Resolve a path inside Raw/, refusing to escape."""
    base = RAW.resolve()
    target = (base / rel).resolve()
    if not target.is_relative_to(base) \
            or not target.is_file():
        return None
    return target


# --------------------------------------------------------------
@app.route("/raw/<path:rel>")
def raw_page(rel):
    """Show one source: Markdown, text, or the file."""
    target = resolve_raw(rel)
    if target is None:
        abort(404)
    if target.suffix.lower() not in (".md", ".txt"):
        return send_file(target)
    idx = wp.page_index(ROOT)
    text = target.read_text(encoding="utf-8",
                            errors="replace")
    if target.suffix.lower() == ".txt":
        content = f"<pre>{html.escape(text)}</pre>"
    else:
        meta, body = wp.split_frontmatter(text)
        content = infobox(meta) + md.markdown(
            body, extensions=MD_EXTS)
    head = (f"<h1>{html.escape(target.name)}</h1>"
            '<div class="pagetype">Raw source (read-only)'
            f" &middot; {anchor('/raw/', 'all sources')}"
            "</div>")
    return shell(target.name, head + content, idx)


# --------------------------------------------------------------
def snippet(text, pos, qlen):
    """HTML excerpt around a match, match in bold."""
    start, end = max(0, pos - 80), pos + qlen + 80
    return ("..." + html.escape(text[start:pos])
            + f"<b>{html.escape(text[pos:pos + qlen])}</b>"
            + html.escape(text[pos + qlen:end]) + "...")


# --------------------------------------------------------------
def search_hits(q):
    """Ranked (score, page, snippet): titles first."""
    ql, hits = q.lower(), []
    for page in wp.pages(ROOT):
        text = page.text()
        count = text.lower().count(ql)
        in_title = ql in page.name.lower()
        if not count and not in_title:
            continue
        pos = max(text.lower().find(ql), 0)
        score = (100 if in_title else 0) + count
        hits.append((score, page, snippet(text, pos, len(q))))
    hits.sort(key=lambda h: (-h[0], h[1].name))
    return hits


# --------------------------------------------------------------
@app.route("/search")
def search():
    """Full-text, case-insensitive search of all pages."""
    idx = wp.page_index(ROOT)
    q = request.args.get("q", "").strip()
    if not q:
        return shell("Search", "<h1>Search</h1><p>Type a "
                     "query above.</p>", idx)
    hits = search_hits(q)
    out = [f"<h1>Search: {html.escape(q)}</h1>"
           f"<p>{len(hits)} pages found</p>"]
    for _, page, snip in hits:
        out.append(
            f'<div class="result"><b>'
            f"{anchor(page_url(page.name), page.name)}</b>"
            f" <small>({page.section})</small><br>"
            f'<span class="snippet">{snip}</span></div>')
    return shell(f"Search: {q}", "".join(out), idx, q)


# --------------------------------------------------------------
@app.errorhandler(404)
def not_found(_err):
    """Friendly 404 page."""
    idx = wp.page_index(ROOT)
    body = ("<h1>Page not found</h1><p>Try the "
            f'{anchor(page_url("Index"), "Index")} or the '
            "search box.</p>")
    return shell("Page not found", body, idx), 404


# --------------------------------------------------------------
if __name__ == "__main__":
    if not ROOT.is_dir():
        sys.exit(f"No wiki at {ROOT}")
    print(f"Serving wiki: {ROOT}")
    print(f"Open: http://localhost:{PORT}")
    app.run(host="127.0.0.1", port=PORT)
