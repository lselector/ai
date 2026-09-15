#!/usr/bin/env python3
"""Command-line tools for a project wiki (OKF Markdown).

Stdlib-only. Agents and humans use it to create,
search, lint and index the wiki in <repo>/wiki.

Usage (T = ~/.claude/wiki/wiki_tools.py):
    python3 T init                  # create wiki skeleton
    python3 T find "Wiki/Concepts/*"
    python3 T grep "rate limit"     # add --regex for regex
    python3 T read Wiki/Entities/Postgres.md
    python3 T backlinks Postgres    # who links to a page
    python3 T index                 # rebuild Index.md
    python3 T log "Added [[Postgres]] entity page."
    python3 T check                 # exit 1 on errors
    python3 T where                 # print the wiki root

The wiki root is the nearest wiki/ folder found walking
up from the current directory to the git repo root, or
<repo>/wiki if none exists yet. Override with the
WIKI_ROOT environment variable.

Created: 2026-09-15
Last updated: 2026-09-15
"""

import argparse
import sys

import wiki_edit as we
import wiki_pages as wp


# --------------------------------------------------------------
def cmd_check(root, _args):
    """Print lint results; exit 1 when there are errors."""
    if not root.is_dir():
        print(f"No wiki at {root}; run init")
        return 1
    errors, warnings = wp.check(root)
    for e in errors:
        print(f"ERROR {e}")
    for w in warnings:
        print(f"WARN  {w}")
    print(f"{len(wp.pages(root))} pages, {len(errors)} "
          f"errors, {len(warnings)} warnings")
    return 1 if errors else 0


# --------------------------------------------------------------
def cmd_init(root, _args):
    """Create the wiki skeleton."""
    made = we.init(root)
    print(f"Wiki root: {root}")
    for name in made:
        print(f"  created {name}")
    if not made:
        print("  nothing to do, skeleton already exists")
    return 0


# --------------------------------------------------------------
def run_command(root, args):
    """Dispatch the simple commands; return exit code."""
    if args.cmd == "find":
        out = wp.find(args.arg or "*", root)
    elif args.cmd == "grep":
        out = wp.grep(args.arg, root, regex=args.regex)
    elif args.cmd == "read":
        out = [wp.read(args.arg, root)]
    elif args.cmd == "backlinks":
        out = [wp.rel(p.path, root)
               for p in wp.backlinks(args.arg, root)]
    elif args.cmd == "index":
        out = [f"wrote {we.build_index(root)}"]
    elif args.cmd == "log":
        out = [f"logged in {we.append_log(root, args.arg)}"]
    else:
        out = [str(root)]
    print("\n".join(out))
    return 0


# --------------------------------------------------------------
def parse_args(argv):
    """Parse 'command [argument] [--regex]'."""
    ap = argparse.ArgumentParser(
        description="Project wiki tools.",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("cmd", choices=[
        "init", "find", "grep", "read", "backlinks",
        "index", "log", "check", "where"])
    ap.add_argument("arg", nargs="?", default="")
    ap.add_argument("--regex", action="store_true",
                    help="treat the grep query as a regex")
    args = ap.parse_args(argv)
    needs_arg = {"grep", "read", "backlinks", "log"}
    if args.cmd in needs_arg and not args.arg:
        ap.error(f"'{args.cmd}' needs an argument")
    return args


# --------------------------------------------------------------
def main(argv=None):
    """Entry point; returns the process exit code."""
    args = parse_args(argv)
    root = wp.get_root()
    special = {"check": cmd_check, "init": cmd_init}
    if args.cmd in special:
        return special[args.cmd](root, args)
    if args.cmd != "where" and not root.is_dir():
        print(f"No wiki at {root}; run init")
        return 1
    return run_command(root, args)


# --------------------------------------------------------------
if __name__ == "__main__":
    sys.exit(main())
