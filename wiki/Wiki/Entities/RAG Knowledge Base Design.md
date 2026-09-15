---
type: Document
title: RAG Knowledge Base Design
description: The 2026 draft architecture for an AI agent knowledge base over millions of documents at a financial company.
tags: [rag, design, architecture]
timestamp: 2026-09-15T00:00:00Z
---

# RAG Knowledge Base Design

A design document in `rag2026/` for a RAG system over
about three million files at a financial company. Status
as of its 2026-08-27 date: draft, pending approval. It is
written as a story in 23 chapters, with formal appendices
for requirements, technology choices and risks.

## Main decisions

- One PostgreSQL 16+ server is the system of record. It
  holds the document registry, entitlements, vector
  search (`pgvector`, HNSW), BM25 keyword search
  (`pg_search`), the job queue (`SKIP LOCKED`), agent
  memory and the audit log. There is no vector database,
  broker or graph database. See [[Simplicity Principle]].
- The corpus comes to roughly 20 to 25 million chunks,
  small enough for one well-provisioned server. Scaling
  gates (over 50 million chunks, p95 latency over 2
  seconds after tuning) say when to add specialized
  infrastructure.
- Documents sit on a mounted filesystem, not in an object
  store. Parsing uses Docling with PyMuPDF as the fast
  path, and happens once.
- Retrieval combines vectors, BM25 and the document graph,
  then reranks with a cross-encoder. Access control is
  applied in SQL before ranking. A bounded multi-step loop
  allows up to 4 passes.
- Python over Rust, because the heavy work already runs in
  C and on GPUs.
- Vanilla JavaScript front end, no build step.
- Failures become "monkeys": tasks with an owner and a
  history.
- Dependencies must be at least 30 days old and pinned.

It is a scaled-up answer to the same problem as the
[[RAG Demo App]]. The companion `design-doc-how-to.md`
turns the process into a general method, which became the
`design-doc` skill in the [[dot_claude Setup]].

## Sources

- `rag2026/rag-knowledge-base-design.md` (Principles,
  "The Temptation of Shiny Infrastructure", Appendix B)
- `rag2026/README.md`
- `rag2026/design-doc-how-to.md`
- Related: [[Retrieval Augmented Generation]]
