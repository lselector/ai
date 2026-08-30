---
name: design-doc
description: Create and iteratively evolve a design document for a software project — formal spec first, then Q&A-driven refinement, optional story-style rewrite for human readability, and polished PDF output. Use when the user asks to create, review, improve, or rewrite a design document, architecture document, or technical proposal.
---

# Creating a Software Design Document

This skill guides an iterative, conversation-driven process for producing a design document that is technically rigorous **and** genuinely readable. It was distilled from a real project (a RAG knowledge base for millions of documents) that went from formal spec to story-style document over ~11 iterations.

The core insight: a design document is not written in one pass. It evolves through cycles of **question → clarification → fold the clarification back into the document**. The user's questions are your best signal for what the document fails to explain.

## Ground Rules (apply to every phase)

1. **Propose before editing.** When the user asks "does it make sense to…" or "can we improve…", they want your assessment, not immediate changes. Present proposals with clear recommendations; edit only when told (e.g. "OK, please update the document", "add as you see fit").
2. **Answer questions in plain language first.** When the user is confused ("is the wiki stored in files or in the database?"), answer conversationally with analogies and concrete examples — don't just point at the document. Then consider whether the confusion reveals a gap worth fixing in the document itself.
3. **Preserve before destructive rewrites.** Before a major restructuring (e.g. formal → story style), save the current version under a distinct name (e.g. `<name>-formal.md`) if it isn't committed to git. Tell the user where the backup is.
4. **Verify claims against the actual document.** When asked "please confirm the design does X", read the document and cite the specific sections/lines. If it doesn't do X, say so plainly.
5. **Fact-check external references.** If the user names a format, standard, or project you can't verify (e.g. a format name that doesn't exist), flag it honestly and propose the real, established equivalent.
6. **Keep every artifact regenerable.** Markdown is the source of truth; PDFs, HTML, and diagrams are projections rebuilt from it.

## Phase 1 — The Formal Specification

Structure the document with these sections (adapt to the project; cut what doesn't apply):

1. **Title + status line** (`Status: Draft (pending approval) · Date: …`). No version numbers in file names; no changelog at the top — git is the changelog.
2. **Executive summary** — 3–5 short paragraphs: the scale/scope headline, the key methods or architecture bets, the resource footprint. Write it last, place it first.
3. **Purpose** — the problem and the constraints (compliance, security, scale).
4. **Requirements tables with stable IDs** — Functional (F1…), Security/Compliance (S1…), Non-Functional (N1… with measurable targets: latency percentiles, RPO/RTO, SLAs). IDs make review and cross-referencing possible.
5. **Explicit non-goals** — what v1 deliberately does NOT do. As load-bearing as the requirements.
6. **Design principles** — numbered, quotable. Always consider including:
   - **Simplicity as the guiding principle**: the fewest moving parts that still deliver the functionality. Simplicity makes the project do-able, flexible, maintainable, affordable — fast to prototype, small team, no heavy hardware. Complexity in architecture and infrastructure can bring a project to its knees; treat it as the primary project risk.
   - **One system of record** — consistency as a transaction, not a distributed-systems project.
   - **Expensive work once; derived artifacts disposable** (parse once / index many; views are projections, never hand-edited).
   - **Add components only when evaluation demands it** — with quantitative **scaling gates** (explicit thresholds at which specialized infrastructure becomes justified). Bets should be falsifiable.
7. **Architecture sections** — storage, data model (with actual DDL/schemas), processing pipeline, retrieval/serving, plus — these are commonly forgotten:
   - **Lifecycle**: what happens to every derived artifact when data is added / updated / removed. Include a propagation matrix (event × artifact → refresh mechanism and latency), consistency rules (soft-deletion for auditability, atomic visibility flips), and propagation SLAs.
   - **Continuous evaluation**: a golden test suite, a nightly/post-update quality gate with regression thresholds that page and freeze on failure, reconciliation counts to catch silent pipeline failures, and (for AI systems) hallucination measurement with an unanswerable-question set.
   - **Backup & recovery**: what's irreplaceable vs. reconstructible (data tiers), RPO/RTO, restore ordering, and scheduled restore testing. "Replicas are not backups."
8. **Technology choices table** — layer / selection / rationale.
9. **Sizing estimates** — disk, database, memory, growth rates, backup overhead, in tables with the arithmetic shown (`3M docs × ~1 MB ≈ 3 TB`). Users always ask; pre-empt it.
10. **Roadmap** — phases with timeframes; trust-building work (evaluation, sign-offs, DR drills) scheduled before scale-out.
11. **Risk matrix** — risk / impact / engineered mitigation with section references.
12. **Summary.**

Include diagrams (SVG) for: overall architecture, data layout, main workflow, roadmap.

## Phase 2 — Iterate Through Dialogue

Expect and welcome these recurring moves; each has a right response:

- **"Confirm the design does X"** → verify against the text, cite sections.
- **"Would it make sense to add Y?"** → assess honestly: what's already covered, what's a real gap, what's marginal. Rank proposals by value/cost. Wait for the go-ahead.
- **"So we will have A, B, C, D — correct?"** → confirm with a mapping table (user's term → design's term → status), and clarify relationships between layers the user sees as separate.
- **"Can we borrow from project Z?"** (user shares a URL) → fetch and study it, then map its techniques into three buckets: *already covered* (say where), *worth adopting* (concrete schema/API changes), *marginal* (mention, don't build). Note domain differences that limit transfer.
- **"Update the document per our conversation"** → integrate everything discussed consistently: requirements rows, principles, sections, tech table, roadmap, risk matrix, cross-references. Renumber carefully; fix all references to renumbered sections.

## Phase 3 — Readability Pass

When the formal draft is content-complete:

- Executive summary at top; changelog and file-name version numbers removed.
- **Table of contents** with working anchor links (verify anchors resolve in both GitHub and the PDF build).
- Consistent cross-references (§x.y); no dangling references to removed material (e.g. "v4 adds…" after the changelog is gone).

## Phase 4 — Optional Story Rewrite

If the user finds the formal style hard to consume, offer a **story-style rewrite**: the same technical substance told as a narrative of challenges converted into solutions.

- Each section = one concrete challenge, opened vividly (a scene, a failing query, an uncomfortable truth), resolved into the design decision with its rationale and numbers intact.
- **Do not use "Prologue", "Chapter N", "Epilogue" labels** — plain evocative headings only ("The Day Everything Goes Wrong", "What Was True Last March?").
- Cross-reference sections by name or idea, never by number ("remember this when we get to the recovery story").
- Close with "the design in N decisions" — a distillation list, simplicity first.
- Keep the formal reference material (requirement tables, tech choices, risk register) as compact **appendices**.
- Keep both files: story version as the main document, formal version alongside for implementers/approvers.

Story-style prose rules: concrete numbers over adjectives; short declarative sentences for the punches ("Nobody can find it."); explain *why* before *what*; tables only for genuinely tabular data.

## Phase 5 — PDF Generation

Target: US Letter, 0.7" margins (or as requested). A proven pipeline with no LaTeX dependency:

1. `pandoc -f gfm -t html5 --standalone --css=<style.css>` → HTML, then **WeasyPrint** → PDF.
2. CSS: `@page { size: Letter; margin: 0.7in; }` + page counters in margin boxes, running header suppressed on page 1, `header#title-block-header { display: none; }` (pandoc duplicates the title), `tr { page-break-inside: avoid; }`, `page-break-after: avoid` on headings, wrapped `pre` blocks, compact styled tables.
3. **Rasterize SVG diagrams** — WeasyPrint mangles SVGs with embedded font styles. Use headless Chrome: `--headless --screenshot=<out.png> --window-size=<w>,<h> --force-device-scale-factor=4` on each SVG; swap `.svg` → `.png` references with `sed` at build time only (Markdown keeps SVGs for GitHub/Obsidian).
4. **Verify the output**: page count and size, visually inspect the title page, a table-heavy page, and every figure page; check TOC anchors resolve (`href="#…"` vs `id="…"` in the built HTML); grep the extracted PDF text for the newly added sections.
5. Keep the CSS in the repo (e.g. `.pdf-style.css`) and document the rebuild one-liner. Regenerate the PDF after every content change the user asks for.

Also fix mechanical issues discovered along the way (corrupted escape sequences like `\r`/`\t` eaten from `$\rightarrow$`, image paths pointing at directories that don't exist — move files or fix paths via `git mv`).

## Definition of Done

- The document answers scale, cost, and "how big" questions with numbers.
- Simplicity is stated as a principle, and every component earns its place against it.
- Lifecycle (add/update/remove propagation) and continuous evaluation are described, not just steady-state architecture.
- A newcomer can read the story version in one sitting; an implementer can build from the formal version + appendices.
- The PDF is regenerated, verified, and matches the Markdown.
