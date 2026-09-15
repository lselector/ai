#!/bin/bash
# Start the wiki web server for a project, in the background.
#
# Usage:
#   ~/.claude/wiki/server_start.sh [wiki_dir]
#   PORT=8021 ~/.claude/wiki/server_start.sh
#   PYTHON=/path/to/python ~/.claude/wiki/server_start.sh
#
# wiki_dir defaults to the nearest wiki/ folder above the
# current directory. Port defaults to 8020. If a wiki
# server started by these scripts already holds the port,
# it is stopped first, so start doubles as restart. A port
# held by any other program is left alone.
# PID and log files: ~/.claude/wiki/run/<port>.{pid,log}

HERE="$(cd "$(dirname "$0")" && pwd)"
PORT="${PORT:-8020}"
RUN="$HERE/run"
PIDFILE="$RUN/$PORT.pid"
LOGFILE="$RUN/$PORT.log"
mkdir -p "$RUN"

find_wiki() {
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        [ -d "$dir/wiki" ] && { echo "$dir/wiki"; return; }
        [ -e "$dir/.git" ] && return
        dir="$(dirname "$dir")"
    done
}

pick_python() {
    local candidates=("$PYTHON")
    [ -z "$PYTHON" ] && candidates=(python python3 \
        "$HOME"/.venvs/*/bin/python)
    for p in "${candidates[@]}"; do
        command -v "$p" > /dev/null 2>&1 || continue
        if "$p" -c "import flask, markdown" 2>/dev/null
        then
            command -v "$p"
            return
        fi
    done
}

WIKI="${1:-${WIKI_ROOT:-$(find_wiki)}}"
if [ -z "$WIKI" ] || [ ! -d "$WIKI" ]; then
    echo "No wiki/ folder found. Create one with:"
    echo "  python3 $HERE/wiki_tools.py init"
    exit 1
fi
WIKI="$(cd "$WIKI" && pwd)"

PY="$(pick_python)"
if [ -z "$PY" ]; then
    echo "No python with flask and markdown found."
    echo "Install: pip install flask markdown"
    echo "Or set PYTHON=/path/to/python"
    exit 1
fi

PORT="$PORT" "$HERE/server_stop.sh" --quiet

if lsof -ti "tcp:$PORT" -sTCP:LISTEN > /dev/null 2>&1; then
    echo "Port $PORT is used by another program."
    echo "See: lsof -i :$PORT   Or try: PORT=8021 $0"
    exit 1
fi

nohup "$PY" "$HERE/wiki_server.py" "$WIKI" \
    > "$LOGFILE" 2>&1 &
echo $! > "$PIDFILE"

for _ in 1 2 3 4 5 6 7 8 9 10; do
    sleep 0.5
    kill -0 "$(cat "$PIDFILE")" 2>/dev/null || break
    if lsof -ti "tcp:$PORT" -sTCP:LISTEN > /dev/null 2>&1
    then
        echo "Wiki server started (pid $(cat "$PIDFILE"))"
        echo "Wiki: $WIKI"
        echo "Open: http://localhost:$PORT"
        echo "Log:  $LOGFILE"
        exit 0
    fi
done

echo "Server failed to start. Last log lines:"
tail -5 "$LOGFILE"
kill "$(cat "$PIDFILE")" 2>/dev/null
rm -f "$PIDFILE"
exit 1
