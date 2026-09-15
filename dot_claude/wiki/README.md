# Project wiki tools

Shared tools that give every project a persistent
knowledge base in `<repo>/wiki/`: interlinked Markdown
pages in Open Knowledge Format (OKF). Agents search it
with find and grep. People browse it as a local
Wikipedia-style site.

The design follows the context wikis in
`~/Documents/GitHub/context-wiki/` and
`~/Documents/GitHub/infra_book/`, made generic so it
works in any repo.

## Pieces

| Piece | Where |
|---|---|
| Rule: when to read, create and update the wiki | `~/.claude/rules/update_wiki.md` |
| Format and layout reference | [conventions.md](conventions.md) |
| Skill: create a wiki and seed first pages | `~/.claude/skills/wiki-init/` |
| Skill: file new knowledge, ripple links, lint | `~/.claude/skills/wiki-update/` |
| Skill: start or stop the web UI | `~/.claude/skills/wiki-serve/` |

## Files here

- [wiki_tools.py](wiki_tools.py) - command-line entry:
  `init`, `find`, `grep`, `read`, `backlinks`, `index`,
  `log`, `check`, `where`. Stdlib only.
- [wiki_pages.py](wiki_pages.py) - read side: layout,
  frontmatter parser, links, search, lint. Stdlib only.
- [wiki_edit.py](wiki_edit.py) - write side: skeleton,
  generated Index, Log entries. Stdlib only.
- [wiki_server.py](wiki_server.py) - read-only web UI
  (Flask + markdown).
- [styles.css](styles.css) - the web UI's only
  stylesheet.
- `server_start.sh`, `server_stop.sh`,
  `server_restart.sh` - run the web UI in the
  background.
- [test_wiki.py](test_wiki.py) - unit tests.
- `run/` - PID and log files of running servers,
  one pair per port.

Dependencies: `wiki_server.py` imports `wiki_pages.py`;
`wiki_tools.py` imports `wiki_pages.py` and
`wiki_edit.py`. Nothing imports the server.

## Quick start

```bash
cd ~/Documents/GitHub/myproject
python3 ~/.claude/wiki/wiki_tools.py init
python3 ~/.claude/wiki/wiki_tools.py check
~/.claude/wiki/server_start.sh       # http://localhost:8020
~/.claude/wiki/server_stop.sh
```

Or in Claude Code: `/wiki-init`, `/wiki-update`,
`/wiki-serve`.

## Finding the wiki root

All tools look for the nearest `wiki/` folder, walking
up from the current directory and stopping at the git
repo root. With no wiki yet, `init` creates
`<repo root>/wiki`. Set `WIKI_ROOT=/path/to/wiki` to
point anywhere else, including older wikis with the
same layout under another name, for example
`WIKI_ROOT=~/Documents/GitHub/infra_book/Context-Wiki-Infra`.

## Web UI

`server_start.sh [wiki_dir]` starts `wiki_server.py` in
the background on port 8020. Set `PORT=8021` to run a
second project's wiki at the same time. Starting on a
port that already runs a wiki server restarts it.
A port held by any other program is left alone, and
the script exits with a message. The stop script kills
only `wiki_server.py` processes.

The script uses `$PYTHON` if set, otherwise the first
of `python`, `python3`, `~/.venvs/*/bin/python` that
can import flask and markdown
(`pip install flask markdown`).

Pages:

- `/` - `Dashboards/Home.md` if present, else the Index
- `/wiki/<Page Name>` - a page with infobox and
  "What links here"
- `/section/<Concepts|Entities|Summaries|Dashboards>`
- `/raw/` and `/raw/<path>` - read-only sources
- `/search?q=...` - full-text search, title hits first

The server binds to 127.0.0.1 and never writes files.
Pages are re-read on every request.

## Tests

```bash
~/.venvs/standard/bin/python ~/.claude/wiki/test_wiki.py
```

With plain `python3` (no flask) the server test is
skipped.

---

Created: 2026-09-15
Last updated: 2026-09-15
