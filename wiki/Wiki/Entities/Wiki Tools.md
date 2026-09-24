---
type: Module
title: Wiki Tools
description: Stdlib Python CLI and Flask web UI that create, lint, index and serve OKF project wikis like this one.
tags: [wiki, tooling, okf]
timestamp: 2026-09-15T00:00:00Z
---

# Wiki Tools

The tooling behind this wiki. The source lives in
`dot_claude/wiki/` and is installed at `~/.claude/wiki/`,
where the `wiki-*` skills call it. Pages use Google's Open
Knowledge Format: YAML frontmatter plus Markdown with
double-bracket wikilinks.

## Files

- `wiki_tools.py`: the CLI. `init`, `where`, `find`,
  `grep`, `read`, `backlinks`, `index`, `log`, `check`.
  Stdlib only.
- `wiki_pages.py`: read side (layout, frontmatter,
  links, search, lint).
- `wiki_edit.py`: write side (skeleton, Index, Log).
- `wiki_server.py`: read-only web UI on port 4747,
  needs `flask` and `markdown`.
- `server_start.sh`, `server_stop.sh`,
  `server_restart.sh`, `test_wiki.py`.

Imports go one way: the CLI and the server both use
`wiki_pages.py`, and nothing imports the server.

## Behaviour worth knowing

- The tools find the nearest `wiki/` walking up from the
  current directory, stopping at the git root.
  `WIKI_ROOT` overrides this.
- `init` never overwrites existing files.
- `check` exits 1 on errors (missing folder, page with no
  `type`, duplicate page name). Dangling links and
  orphans are only warnings.
- The design is a generic version of the context wikis in
  the `context-wiki` and `infra_book` repos.

Part of the [[dot_claude Setup]].

## Sources

- `dot_claude/wiki/README.md`
- `dot_claude/wiki/conventions.md`
