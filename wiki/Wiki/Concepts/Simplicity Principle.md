---
type: Principle
title: Simplicity Principle
description: Use the fewest moving parts that still deliver the full functionality; add components only when a written scaling gate trips.
tags: [principle, architecture]
timestamp: 2026-09-15T00:00:00Z
---

# Simplicity Principle

The main design rule in this repo. Choose the simplest
architecture that still does the whole job, and make any
added component justify itself with evidence. It is a
global Claude Code rule and the first principle of the
[[RAG Knowledge Base Design]].

## What it looks like in practice

- One well-understood system instead of several
  specialized ones. In the RAG design that is a single
  PostgreSQL server instead of a vector database, search
  cluster, broker, workflow engine and graph database.
- No distributed architecture: one server with a standby,
  files on a mounted filesystem.
- Scaling gates: written, measurable thresholds that must
  trip before new infrastructure comes in.
- Boring technology the team already knows, and no
  flexibility added for imagined future needs.

It does not permit cutting correctness, security or
auditability. The target is the simplest thing that
fully works.

The companion rule is modularity: small modules behind
ports, dependencies pointing one way, concrete adapters
wired in one composition root. The design document
illustrates it with dumplings on a plate that must not
fuse together.

## Sources

- `dot_claude/rules/simplicity.md`
- `dot_claude/rules/modularity.md`
- `rag2026/rag-knowledge-base-design.md` (The Principles)
- [[dot_claude Setup]]
