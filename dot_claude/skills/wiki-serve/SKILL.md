---
name: wiki-serve
description: Start, stop or restart the local web UI for the project's knowledge-base wiki (Wikipedia-style browsing with search, infoboxes and backlinks, on http://localhost:8020). Use when the user asks to open, browse, serve, view, start or stop the wiki website or wiki server.
---

# Serve the project wiki in a browser

Scripts live in `~/.claude/wiki/`. Arguments to this
skill: `start` (default), `stop`, `restart`, optionally
followed by a port number.

## Start

Run from inside the project (any subfolder works):

```bash
~/.claude/wiki/server_start.sh
```

- Another port: `PORT=8021 ~/.claude/wiki/server_start.sh`.
  Use one when a different project's wiki should keep
  running on 8020.
- A wiki at another path:
  `~/.claude/wiki/server_start.sh /path/to/wiki`.

The script finds the nearest `wiki/`, picks a python
that has flask and markdown, restarts a wiki server
already on that port, and refuses a port held by any
other program.

## Stop or restart

```bash
~/.claude/wiki/server_stop.sh          # PORT=... for others
~/.claude/wiki/server_restart.sh
```

## Troubleshooting

- "No wiki/ folder found": offer `/wiki-init`.
- "No python with flask and markdown": tell the user
  to run `pip install flask markdown` in their python,
  or set `PYTHON=/path/to/python`. Do not install
  packages without asking.
- "Port ... used by another program": retry with the
  next port, e.g. `PORT=8021`.
- Failed start: read `~/.claude/wiki/run/<port>.log`.

## Report

Give the URL (`http://localhost:<port>`) and the wiki
path in one or two lines. Pages reload from disk on each
request, so edits show without a restart.
