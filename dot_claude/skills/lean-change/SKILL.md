---
name: lean-change
description: Implement a feature or fix without bloating the code - find where it belongs, reuse what exists, gate any new dependency, then run a tidy pass over the diff to delete duplicates, dead code and leftovers before reporting. Use when the user asks to add a feature "cleanly", "without bloat", "the lean way", or for any non-trivial change to a project that has grown by many small AI-made edits. Applies the no_frankenstein rule as a step-by-step procedure.
---

# Lean change

Procedure form of `~/.claude/rules/no_frankenstein.md`.
Goal: the finished diff looks as if the feature was part of
the original design. Small on purpose: three steps plus a
report.

## 1. Before writing code

1. **Read the neighborhood.** Open the README, the wiki
   (if `wiki/` exists), and the modules the feature touches.
   Name the module that should own the feature.
2. **Search for reuse.** Grep for functions, helpers and
   patterns that already do part of the job. List what you
   will reuse.
3. **Does it fit?** If the feature does not fit the current
   structure, plan a small preparatory refactor first, as
   its own step, with tests passing before the feature goes
   in. If that refactor is large, stop and ask the user.
4. **Dependency gate.** For each package you want to add,
   answer in one line each:
   - Can the standard library do it?
   - Can an installed dependency do it?
   - Is plain code under ~30 lines enough?
   - Is the package maintained, small, license-compatible?

   Add it only if the first three are "no" and the last is
   "yes".

## 2. Implement

Write the minimum that works, in the owning module, using
the existing patterns of that codebase. Follow the project
and global formatting rules.

## 3. Tidy pass over the diff

Run `git diff` (plus `git status` for new files) and check
every hunk:

- [ ] No logic duplicated from elsewhere in the repo.
- [ ] No second way of doing something the code already
      does.
- [ ] No dead code, unused imports, debug prints,
      commented-out blocks, or leftover experiments.
- [ ] Code the change made obsolete is deleted, not kept
      beside the new version.
- [ ] Nothing left from rejected variants tried while
      debugging: their code, guards, retries, flags,
      scratch files, or comments about them (see "Vacuum
      before done" in the rule).
- [ ] Packages the change made unused are removed from the
      manifest.
- [ ] No wrapper or `try/except` hiding a root cause.
- [ ] Names say what things are; no `utils2`, `new_`,
      `_v2`, `temp`.
- [ ] Size limits hold for files and functions.
- [ ] Tests pass; README, docs and wiki updated if the
      change affects them.

Fix what fails, then re-run the tests.

## 4. Report

Two to four lines: what changed, what was reused, what was
deleted, any dependency added and why. If you noticed a
warning sign from the rule that the change did not fix,
name it in one line and suggest `/architecture-review`.
Do not commit unless asked.
