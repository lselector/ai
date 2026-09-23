# No Frankenstein Code

Software built by many small AI-made changes tends to turn
into a Frankenstein creature. Each change takes the quickest
path: a new library, a copied helper, a special case bolted
onto the side. Each one looks fine alone. Together they make
code that is ugly, bloated and slow, with several ways of
doing the same job.

Every change must leave the code looking as if the feature
had been planned from the start. This rule adds to
`simplicity.md` and `modularity.md`; it does not repeat them.

## On every change

- **Fit, don't bolt on.** Extend the structure that is
  already there. If the feature does not fit, reshape the
  structure first (a small refactor), then add the feature.
  Never build a parallel path next to the old one.
- **Reuse before writing.** Search for an existing function,
  pattern or module that does the job. Never add a second
  way of doing one thing: two HTTP clients, two config
  loaders, two date libraries, two logging styles.
- **Dependencies must pay rent.** Before adding a package,
  check whether the standard library, an installed
  dependency, or 30 lines of plain code would do. If the
  package is still needed, it must be maintained, small,
  and license-compatible. Pin it and say in the reply why
  it was added. Never add a package to save a few lines.
- **Delete what the change made obsolete.** See "Vacuum
  before done" below. This is not optional.
- **Fix causes, not symptoms.** No wrapper, `try/except`,
  retry or special case that hides a bug. No compatibility
  shims nobody needs.
- **Keep the shape visible.** A new concept gets a name and
  a home in its owning module. Do not let one file or
  function become the place where everything goes.
- **Update docs in the same change** (`update_docs.md`).

## Vacuum before done

Debugging and experiments leave debris. We try variant A,
then B, then C; C works and is kept. A and B must not stay
behind. The code that remains should look as if C had been
written directly, on the first try.

Before calling a task done, re-read the whole diff against
the starting point (not only the last edit) and remove:

- code from rejected variants: unused functions, branches,
  parameters, config keys, classes, files;
- commented-out code and "old version" copies
  (`foo_old`, `foo_v2`, `foo_backup`, `.bak` files);
- debug prints, extra logging, timers, asserts and test
  hooks added only to find the bug;
- `try/except`, retries, sleeps, guards and fallbacks added
  while guessing at the cause that the real fix made
  unnecessary;
- imports, packages, env vars and flags that only a
  rejected variant needed;
- scratch scripts, temp data, notebooks and output files;
- comments and docs that describe a variant we dropped,
  or the debugging story ("tried X, didn't work").

For each line in the diff, ask: does the accepted solution
need this? If not, delete it. If unsure, find out; do not
keep it "just in case". Git history already remembers the
failed attempts, so the code does not need to.

## Warning signs

Watch for these while working:

- the same logic in three or more places;
- a file or function over the size limits;
- one module importing half the app;
- a small feature needing edits in many files;
- dependency count growing faster than features;
- "temporary" code that survived several changes;
- different patterns used for the same job.

When you see one, do not start a large refactor in the
middle of a feature. Name the problem in one line in your
reply and suggest `/architecture-review`.

## Report

If a change adds a dependency, adds a module, or leaves
known debt behind, say so in one line in the reply. If the
vacuum pass removed leftovers, say so in one line too.
