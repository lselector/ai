# rag2026

Design work for an AI agent knowledge base (RAG) over millions of
documents — plus the reusable method for producing design documents
like it.

## Files

| File | What it is |
|---|---|
| [`rag-knowledge-base-design.md`](rag-knowledge-base-design.md) | The design document itself — story style, with formal appendices (requirements, technology choices, risk register) |
| `rag-knowledge-base-design.pdf` | Rendered PDF (US Letter, 0.7" margins). Regenerated from the Markdown after every change |
| [`how_to_create_a_design_doc.md`](how_to_create_a_design_doc.md) | **Generic guide** — how to write an architecture design document for *any* system: guiding principles, section skeleton, story style, prompt playbook, PDF pipeline |
| [`myprompts.md`](myprompts.md) | The raw prompt log that produced the design document. Source material for the guide |
| `.pdf-style.css` | Print stylesheet for the PDF build |
| `assets/` | Diagrams — SVG for Markdown/GitHub, PNG rasterizations for the PDF |

## Rebuilding the PDF

Markdown is the source of truth; the PDF is a projection.

```bash
pandoc -f gfm -t html5 --standalone --css=.pdf-style.css \
       rag-knowledge-base-design.md -o build/design.html
weasyprint build/design.html rag-knowledge-base-design.pdf
```

SVG references are swapped to their `.png` rasterizations at build
time only — see [`how_to_create_a_design_doc.md`](how_to_create_a_design_doc.md#8-producing-the-pdf)
for the full pipeline and the verification checklist.

## Related

The agent-facing version of this method lives at
`.claude/skills/design-doc/SKILL.md` in the repository root.
