---
name: wiki-update
description: Update the project's knowledge-base wiki (wiki/ folder of OKF Markdown pages) - file new knowledge from the current session, process Inbox/ and new Raw/ sources into summaries, create or extend Concept and Entity pages, ripple links both ways, remove or rename pages safely, then rebuild the index, log and lint. Use when the user asks to update, sync, ingest into, clean up or lint the wiki, and at the end of any task that produced durable project knowledge.
---

# Update the project wiki

Format reference: `~/.claude/wiki/conventions.md`.
`T` below means `python3 ~/.claude/wiki/wiki_tools.py`.

If `T where` shows no wiki exists, run `/wiki-init`
first.

## 1. Baseline

Run `T check`. Note existing errors so you can tell
your changes apart from old ones.

## 2. Collect what is new

Gather candidates from three places:

- **This session.** Decisions made and why, options
  rejected, modules or integrations added or changed,
  bug causes, gotchas, facts the user explained.
  Code-derivable trivia does not count.
- **`Inbox/`.** Each note is either a source (move it to
  `Raw/`, register it) or knowledge (file it into pages,
  then delete the note).
- **`Raw/`.** `check` warns about Raw files that no
  summary cites. Those need summaries. Add a
  `Raw/sources.md` row for any file missing one.

## 3. Summaries (one per Raw source)

Create `Wiki/Summaries/<raw-file-stem>.md`:

```markdown
---
type: Summary
title: <source title>
description: <one sentence: what the source covers>
resource: <original URL, if any>
source_file: Raw/<path/to/file>
tags: [<topic>, summary]
timestamp: <date added>T00:00:00Z
---

# <source title>

<2-4 sentences on what the source says.>

## Key points

- <facts as the source states them, no opinions>

## Related pages

[[Concept A]] · [[Entity B]]
```

## 4. Concepts and Entities

For each subject found in step 2:

1. **Search first**: `T grep "<term>"` and
   `T find "*<Term>*"`, including synonyms and
   abbreviations.
2. **Exists**: extend that page. Add the new fact in the
   right section, date it if it will age, add the source
   to `## Sources`. Correct statements that are now
   wrong instead of appending contradictions.
3. **Missing**: create a flat page in `Wiki/Concepts/`
   (ideas, decisions, patterns, domain terms) or
   `Wiki/Entities/` (named things) with full frontmatter.
   For a decision, use `type: Decision` and cover
   context, the choice, alternatives, consequences.

## 5. Ripple update

For every page you created or changed:

- Link the first mention of each existing page.
- Run `T backlinks "<Page>"` and open the pages that
  link to it: do they still say true things? Update them.
- Add links back from the pages you linked to, where a
  reader of that page would want the pointer.
- Update any dashboard that summarises the area
  (`Home.md`, `Architecture.md`, `Decisions.md`).

## 6. Remove or rename

Remove a page only when it is obsolete, duplicated, or
wrong:

1. `T backlinks "<Page>"` to find every reference.
2. Move unique content into the surviving page.
3. Redirect or delete each link. No dangling links on
   purpose.
4. Delete the page. Leave its Raw source in place unless
   it must be purged; if so, say why in the log.

To rename, create the new file (or `git mv`), replace
`[[Old]]` and `[[Old|` in every backlink, then confirm
`T backlinks "Old"` returns nothing.

## 7. Finish

```bash
T index
T log "<what changed, naming pages as [[links]]>"
T check
```

Zero errors required. Resolve new warnings, or leave a
dangling link only for a page you plan to write, and say
so. Report in 2-4 lines: pages added, changed, removed,
open warnings. Do not commit unless asked.

## Quality bar

- One subject per page; split pages that sprawl.
- Every claim traceable to a summary, code path, or the
  user.
- No secrets, tokens, or personal data.
- Never edit files in `Raw/`.
- Prose per the humanize skill.
