---
name: architecture-review
description: Review a whole codebase's architecture and code for accumulated bloat (the "Frankenstein" effect of many small AI-made changes) and write a ranked list of refactoring recommendations to docs/architecture-review-YYYY-MM-DD.md - duplicated logic, unneeded dependencies, dead code, tangled modules, oversized files, stale docs, and whether the core architecture should change. Read-only until the user picks what to do. Use when the user asks to review, audit, clean up, streamline or refactor the architecture or codebase, asks "what should we refactor", or periodically after many feature changes.
---

# Architecture review

Periodic deep review. Not for every change; that is what
`~/.claude/rules/no_frankenstein.md` and `/lean-change`
are for. Good moments to run it: after 10-20 feature
changes, before a release, or when the rule's warning signs
pile up.

The review is **read-only**. Do not change code until the
user chooses which recommendations to apply.

## 1. Map the system

- Read README, CLAUDE.md, docs, and the wiki if `wiki/`
  exists (start at `wiki/Dashboards/Index.md`).
- List the tree, languages, entry points, and dependency
  manifests (`pyproject.toml`, `requirements*.txt`,
  `package.json`, ...).
- Get file sizes (lines per file, largest first) and churn
  (`git log --since=6.months --name-only --format= | sort |
  uniq -c | sort -rn | head -30`). Big files with high
  churn are the first suspects.
- Sketch the modules and who imports whom. Write it down as
  a short list or a small Mermaid graph.

For a large repo, hand parts of this to Explore subagents
and keep only their conclusions.

## 2. Collect evidence

Use installed tools where they exist, grep where not. Do
not install tools without asking.

| Look for | How |
|---|---|
| Unused dependencies | Python: `deptry`; JS: `knip` or `depcheck`; else grep each package's imports |
| Overlapping dependencies | two libs doing one job (HTTP, dates, config, logging, testing) |
| Dead code | Python: `vulture`, `ruff`; JS: `knip`; else grep for unreferenced names |
| Duplicated logic | similar functions or blocks in different files |
| Import cycles and tangles | import graph from step 1 |
| Oversized files and functions | against the formatting rules' limits |
| Inconsistent patterns | several ways to do errors, config, I/O, logging |
| Workarounds | `try/except` that swallows, `TODO`, `HACK`, `temporary`, retries hiding bugs |
| Stale docs | README and wiki claims the code no longer matches |
| Missing tests | modules with no tests, adapters without integration tests |

Every finding needs evidence: file paths with line
numbers, counts, or tool output.

## 3. Step back: the architecture question

Ask: "If we built this today, knowing everything it now
does, what would the simplest design be?" Compare that to
what exists. Consider:

- components, services or layers that could be removed or
  merged;
- a missing seam (port/adapter) that would untangle a
  vendor dependency;
- data model or storage choices that no longer fit;
- whether a heavy framework or library could be replaced
  by plain code or the standard library.

Propose a core-architecture change only when the evidence
shows the current shape costs more than moving. Say what
it would cost.

## 4. Write the report

Save to `docs/architecture-review-YYYY-MM-DD.md` (create
`docs/` if needed; use today's date). Structure:

```markdown
# Architecture review, YYYY-MM-DD

## Summary
<3-5 sentences: overall health, the biggest problems,
the top recommendations.>

## Current architecture
<module list or Mermaid graph, dependency count,
largest files>

## Recommendations
### R1. <title>
- Problem: <what, with evidence: paths, lines, counts>
- Change: <what to do>
- Benefit: <lines, deps or files removed; what gets easier>
- Risk: <what could break, how tests cover it>
- Effort: S / M / L

## Remove list
<dependencies, files, functions, flags that can simply go>

## Architecture option (only if warranted)
<today's-design sketch, migration steps, cost>

## Keep as is
<things that look odd but are right, and why>
```

Rank recommendations by benefit divided by effort, best
first. Deletions and dependency removals usually win.
Prose per the humanize skill.

## 5. Report and wait

In chat, give the file path and the top 3-5
recommendations in one line each. Ask which ones to apply.

## 6. Applying (only after the user chooses)

- One recommendation at a time, smallest safe steps.
- Run tests after each step. If there are no tests around
  the code being moved, add characterization tests first.
- Behavior must not change unless the recommendation says
  so.
- Update README, docs and wiki as you go; mark each
  recommendation done in the report file.
- Do not commit unless asked.
