---
name: wiki-stop
description: Stop the local web UI server for the project's knowledge-base wiki (default http://localhost:8020). Use when the user asks to stop, shut down, close or kill the wiki website or wiki server.
---

# Stop the project wiki server

Scripts live in `~/.claude/wiki/`. Arguments to this
skill: an optional port number (default 8020), or `all`.

## Stop one port

```bash
~/.claude/wiki/server_stop.sh              # port 8020
PORT=8021 ~/.claude/wiki/server_stop.sh    # another port
```

The script kills only `wiki_server.py` processes on that
port. Other programs on the port are never touched.

## Stop all

For `all`, stop every port that has a pid file:

```bash
for f in ~/.claude/wiki/run/*.pid; do
    [ -e "$f" ] || continue
    PORT="$(basename "$f" .pid)" ~/.claude/wiki/server_stop.sh
done
```

## Report

One line: which port stopped, or that no wiki server was
running there. To start it again, use `/wiki-serve`.
