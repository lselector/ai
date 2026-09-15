# Rules For The Project Wiki

Every project keeps a persistent knowledge base in
`wiki/` at the repo root: interlinked Markdown pages in
Open Knowledge Format (OKF). It is the project's
long-term memory, shared through git.

Tools and the full format live in `~/.claude/wiki/`.
Read `~/.claude/wiki/conventions.md` before writing
wiki pages for the first time in a session.

## Read it

If `wiki/` exists, consult it before researching,
designing, or debugging something that may have been
seen before. Grep it or start at
`wiki/Dashboards/Index.md`, and follow `[[Page Name]]`
links by finding `Page Name.md`. When a page disagrees
with the code, the code wins; fix the page.

## Create it

If there is no `wiki/`, create one with `/wiki-init`
the first time a task produces knowledge worth keeping
(see below). Do not create one for quick questions,
one-line fixes, scratch folders, or when the project's
CLAUDE.md says `wiki: off`. Mention it in your reply
when you create one.

## Update it

Before finishing a task, update the wiki (`/wiki-update`)
if the work produced durable knowledge:

- a design decision and why, including rejected options;
- a new or changed module, service, data model, or
  external integration;
- a non-obvious bug cause, gotcha, or workaround;
- research results, or new sources the user supplied;
- domain terms or requirements the user explained.

Skip it for routine edits that teach nothing new. This
sits beside the README rule: README says how to use
the project, the wiki says what we know about it.

## Always

- Never edit files in `wiki/Raw/`; they are sources.
- Never write secrets or personal data into the wiki.
- Keep `Wiki/Concepts/`, `Wiki/Entities/`,
  `Wiki/Summaries/` flat; one subject per page.
- Link both ways and search before creating a page, so
  there are no duplicates.
- Finish with `python3 ~/.claude/wiki/wiki_tools.py index`,
  a `log` entry, and a `check` with zero errors.
