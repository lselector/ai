---
type: Module
title: dot_claude Setup
description: A copy of the author's ~/.claude folder (rules, skills, wiki tools) kept in the repo as a reusable Claude Code setup.
tags: [claude-code, rules, skills]
timestamp: 2026-09-15T00:00:00Z
---

# dot_claude Setup

`dot_claude/` mirrors `~/.claude/`. It is how the Claude
Code setup gets rebuilt on a new machine or copied into a
new project, and it is what this repo's own `CLAUDE.md`
points to.

## Contents

- `CLAUDE.md` imports every rule with `@rules/<name>.md`.
- `rules/`: one topic per file. Simplicity, modularity,
  Python formatting, terse replies, prose style,
  hyphenated skill names, README upkeep, wiki upkeep, and
  vanilla-JS web development. See [[Simplicity Principle]].
- `skills/`: `design-doc`, `humanize`, `wiki-init`,
  `wiki-update`, `wiki-serve`.
- `wiki/`: the [[Wiki Tools]].

## Install notes

- Global install copies `rules/`, `skills/`, `wiki/` and
  `CLAUDE.md` into `~/.claude/`.
- Per-project install puts rules and skills under
  `<repo>/.claude/`, but `wiki/` still goes to
  `~/.claude/` because the skills call it there.
- Claude Code auto-loads every `.md` in both
  `~/.claude/rules/` and `<repo>/.claude/rules/`. Having
  the same rule in both places loads it twice. Pick one,
  or exclude the project copies with `claudeMdExcludes`.
- `frontend-design` and `remotion-best-practices` are
  third-party skills symlinked from `~/.agents/skills/`
  and are not copied here.

## Sources

- `dot_claude/README.md`
- `CLAUDE.md`
