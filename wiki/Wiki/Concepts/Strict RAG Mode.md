---
type: Concept
title: Strict RAG Mode
description: A chat setting in the RAG demo that forces answers to come only from the uploaded files.
tags: [rag, prompting]
timestamp: 2026-09-15T00:00:00Z
---

# Strict RAG Mode

A switch in the [[RAG Demo App]] chat UI. In strict mode
the model may answer only from the uploaded files. In
non-strict mode the retrieved context is a hint and the
model can fall back on what it already knows.

It is done with prompt text alone, in `do_chat()` in
`demo_RAG/rag_unix/common_tools.py`:

- Strict, context found: the prompt says to answer only
  from the context, and otherwise reply "There is no
  information about it in the document". Chat history
  may also be used.
- Strict, no files or nothing retrieved: the model is
  told to ask the user to upload files.
- Non-strict, context found: the prompt says to answer
  even if the context does not cover the question.
- Non-strict, nothing retrieved: the bare question is
  sent.

Nothing checks the answer afterwards. The model is
trusted to obey the prompt. [[RAG Knowledge Base Design]]
treats this differently: every claim needs a verified
citation, and "I don't know" is graded as a skill.

## Sources

- `demo_RAG/rag_unix/common_tools.py` (`do_chat`)
