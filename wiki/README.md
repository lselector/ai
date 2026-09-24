# ai wiki

Persistent knowledge base for this project: interlinked
Markdown pages in Open Knowledge Format (OKF). Agents
search it with find and grep and follow `[[Page Name]]`
links; people can browse it as a local website.

- `Inbox/` - unsorted notes waiting to be filed.
- `Raw/` - immutable source documents, registered in
  `Raw/sources.md`.
- `Wiki/Summaries/` - one page per Raw source.
- `Wiki/Concepts/` - one page per idea, decision or
  pattern.
- `Wiki/Entities/` - one page per concrete thing:
  module, service, table, tool, vendor.
- `Dashboards/` - `Index.md` (generated), `Log.md`,
  `Topics.md`, and any overview pages.

Every page except `Index.md` and `Log.md` starts with
YAML frontmatter that has at least a `type`. Page names
are file names without `.md` and are unique across the
wiki. Start reading at `Dashboards/Index.md`.

The tools live outside the repo, in `~/.claude/wiki/`:

```bash
python3 ~/.claude/wiki/wiki_tools.py check
~/.claude/wiki/server_start.sh     # http://localhost:4747
```
