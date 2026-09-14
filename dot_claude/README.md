# dot_claude

A copy of my `~/.claude/` setup for Claude Code, kept here
as an example. Use it to rebuild the setup on a new machine
or to seed a new project.

```text
dot_claude/
├── CLAUDE.md        # imports the rules below
├── rules/           # one topic per file, loaded every session
└── skills/
    ├── design-doc/  # /design-doc
    └── humanize/    # /humanize
```

## Recreate globally (all projects on this machine)

```bash
mkdir -p ~/.claude
cp -R dot_claude/rules dot_claude/skills ~/.claude/
cp dot_claude/CLAUDE.md ~/.claude/
```

## Recreate for one project

```bash
mkdir -p <repo>/.claude
cp -R dot_claude/rules dot_claude/skills <repo>/.claude/
```

Then create `<repo>/CLAUDE.md` listing the rules with
`@.claude/rules/<name>.md` (note the `.claude/` prefix;
the global file uses `@rules/<name>.md`).

## Avoid loading rules twice

Claude Code loads every `.md` in `~/.claude/rules/` and in
`<repo>/.claude/rules/` on its own. If the same rule sits in
both places, it lands in context twice. Pick one place per
machine, or skip the project copies with `claudeMdExcludes`
in `~/.claude/settings.json` (use absolute paths). Run
`/context` to see which files loaded.

## Not included

`frontend-design` and `remotion-best-practices` are
third-party skills installed under `~/.agents/skills/` and
symlinked into `~/.claude/skills/`. Reinstall them from
their source instead of copying.
