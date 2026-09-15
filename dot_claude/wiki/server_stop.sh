#!/bin/bash
# Stop the wiki web server on a port (default 8020).
#
# Usage:
#   ~/.claude/wiki/server_stop.sh [--quiet]
#   PORT=8021 ~/.claude/wiki/server_stop.sh
#
# Kills only processes running wiki_server.py: first the
# recorded pid, then any wiki_server.py listening on the
# port. Other programs on the port are never touched.

HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8020}"
PIDFILE="$HERE/run/$PORT.pid"
QUIET="$1"

is_wiki() {
    ps -p "$1" -o command= 2>/dev/null \
        | grep -q "wiki_server.py"
}

say() {
    [ "$QUIET" = "--quiet" ] || echo "$@"
}

PIDS=""
[ -f "$PIDFILE" ] && PIDS="$(cat "$PIDFILE")"
PIDS="$PIDS $(lsof -ti "tcp:$PORT" -sTCP:LISTEN 2>/dev/null)"

STOPPED=""
for PID in $(echo "$PIDS" | tr ' ' '\n' | sort -u); do
    if is_wiki "$PID" && kill "$PID" 2>/dev/null; then
        STOPPED="$STOPPED $PID"
    fi
done
rm -f "$PIDFILE"

if [ -z "$STOPPED" ]; then
    say "No wiki server running on port $PORT"
    exit 0
fi

for _ in 1 2 3 4 5 6 7 8 9 10; do
    lsof -ti "tcp:$PORT" -sTCP:LISTEN > /dev/null 2>&1 \
        || break
    sleep 0.5
done
echo "Stopped wiki server on port $PORT (pid$STOPPED)"
