---
type: Concept
title: Retrieval Augmented Generation
description: Answer a question by first retrieving relevant chunks of your own documents and giving them to the LLM.
tags: [rag, llm]
timestamp: 2026-09-15T00:00:00Z
---

# Retrieval Augmented Generation

RAG answers a question from your own documents. The
documents are split into chunks and embedded as vectors.
The question is embedded the same way, the closest chunks
are retrieved, and the LLM writes an answer from them.

The [[AI Training Curriculum]] lists five steps:

1. Convert the text into vectors in a vector database.
2. Convert the question into a vector.
3. Run a similarity search and retrieve the best matches.
4. Re-rank the findings.
5. Have the LLM turn the findings into a response.

## In this repo

- [[RAG Demo App]] is the teaching version: one process,
  sentence-based chunks, a small embedding model, top 3
  to 5 matches, no re-ranking. See also
  [[Strict RAG Mode]].
- [[RAG Knowledge Base Design]] is the production-scale
  version for millions of documents. It searches three
  ways (vectors, BM25 keywords, a document graph), filters
  by access rights in SQL before ranking, and requires
  cited answers.

## Sources

- `README.md` (Lesson 2)
- `demo_RAG/rag_unix/common_tools.py`
- `rag2026/rag-knowledge-base-design.md`
