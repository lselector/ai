---
type: Module
title: RAG Demo App
description: FastHTML chat app in demo_RAG/rag_unix that answers from uploaded files, with FAISS, ChromaDB or Milvus as the vector store.
tags: [rag, demo, fasthtml]
timestamp: 2026-09-15T00:00:00Z
---

# RAG Demo App

A browser chat app that lets you upload files and ask
questions about them. It lives in `demo_RAG/rag_unix/`
and comes in three copies that differ only in the vector
store.

| Script | Vector store | Top matches |
|---|---|---|
| `rag_faiss.py` | FAISS, in memory | 5 |
| `rag_chromadb.py` | ChromaDB | 3 |
| `rag_milvus.py` | Milvus Lite, file `milvus_demo.db` | 5 |

Each runs on `http://localhost:5001`.

## How it works

`common_tools.py` holds everything shared: the
[[FastHTML]] page, file upload, chat history, and the
chat loop. It converts `.txt`, `.pdf`, `.docx`, `.xlsx`,
`.json` and `.html` to plain text, splits the text into
chunks of 3 sentences with NLTK, and embeds them with the
`all-MiniLM-L6-v2` sentence-transformers model. Replies
stream over a websocket (`/wscon`).

The chat prompt depends on [[Strict RAG Mode]].

## Gotchas

- As of 2026-09 the chat always goes to Claude
  (`claude-sonnet-4-5-20250929`, via `AsyncAnthropic`), so
  `ANTHROPIC_API_KEY` must be set. The comment
  "Always use Claude now" marks the switch. The older
  [[Ollama]] version is kept as `rag_faiss_orig.py`.
- The `start_*.bash` wrappers still refuse to start
  unless `OLLAMA_MODEL` is set and pulled, even though the
  current scripts do not use it.
- The start scripts delete `milvus_demo.db` and
  `uploaded_files/*` on every run.
- The scripts import `levutils.mybag` and
  `levutils.myutils`. Copies of those modules sit in
  `py_utils/`; `levutils` has to be on the Python path.
- Chat state lives in module-level lists, so all browser
  tabs share one conversation.

## Sources

- `demo_RAG/rag_unix/common_tools.py`
- `demo_RAG/rag_unix/rag_faiss.py`,
  `rag_chromadb.py`, `rag_milvus.py`
- `demo_RAG/rag_unix/start_milvus.bash`
- Related: [[Retrieval Augmented Generation]]
