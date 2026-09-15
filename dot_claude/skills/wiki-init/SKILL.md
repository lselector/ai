---
name: wiki-init
description: Create the persistent knowledge-base wiki (wiki/ folder of interlinked OKF Markdown pages) in the current project and seed it with first pages drawn from the README, CLAUDE.md, docs and code. Use when the user asks to create, set up, or start a project wiki or knowledge base, or when the update_wiki rule calls for a wiki and the repo has none.
---

# Create a project wiki

Builds `<repo>/wiki/` and fills it with a small, true
starting set of pages. Format reference:
`~/.claude/wiki/conventions.md` (read it first).

`T` below means `python3 ~/.claude/wiki/wiki_tools.py`.

## Steps

1. **Find the root.** Run `T where`. It prints the
   nearest existing `wiki/`, or `<git root>/wiki` if
   there is none. If the path is not what the user
   expects (not a git repo, wrong folder), stop and ask.
   If a wiki already exists there, say so and switch to
   `/wiki-update` instead.

2. **Create the skeleton.** Run `T init`. It never
   overwrites files.

3. **Learn the project.** Read `README.md`, `CLAUDE.md`,
   any `docs/` folder, the dependency manifest, and the
   top-level source layout. Skim the main entry points.
   Check `git log --oneline | head -30` for recent themes.
   If the user named sources (URLs, PDFs, notes), copy
   them into `Raw/` and register them in
   `Raw/sources.md`.

4. **Write `Dashboards/Topics.md`.** Replace the
   placeholder with 3-8 main topics, each with keywords
   that are likely page names. Keep the frontmatter.

5. **Seed pages.** Only what the material supports; no
   guesses. A good first set is 5-15 pages:
   - Entities for the main modules or services, the data
     stores, and each external system or key library;
   - Concepts for the core domain terms and for design
     decisions whose reasons are written down somewhere;
   - one Summary per file placed in `Raw/`.
   Each page gets frontmatter (`type`, `title`,
   `description`, `tags`), a short lead, `[[links]]` to
   the other seeded pages, and a `## Sources` section
   with code paths or summaries. Write prose per the
   humanize skill.

6. **Optional front page.** For a wiki meant for
   people, write `Dashboards/Home.md` (`type: Dashboard`):
   what the project is, and where to start reading.

7. **Finish.**
   ```bash
   T index
   T log "Seeded the wiki: [[Page A]], [[Page B]], ..."
   T check
   ```
   Fix every ERROR. Fix dangling links and orphans, or
   say why they remain.

8. **README.** Add one line to the project `README.md`
   pointing at `wiki/` (per the update_docs rule), unless
   the project says otherwise.

9. **Report** in a few lines: where the wiki is, pages
   created, open warnings, and that `/wiki-serve` opens
   it in a browser. Do not commit unless asked.
