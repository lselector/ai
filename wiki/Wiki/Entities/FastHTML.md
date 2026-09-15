---
type: Library
title: FastHTML
description: Python web framework built on HTMX, used for the RAG demo and the experiments in fasthtml/.
tags: [web, python, library]
website: https://fastht.ml
timestamp: 2026-09-15T00:00:00Z
---

# FastHTML

A Python framework for web apps from Answer.AI. Pages are
written as Python calls (`Div`, `Ul`, `Form`) and
interactivity comes from HTMX, so there is no separate
JavaScript front end. Install with
`pip install python-fasthtml`.

## In this repo

- `fasthtml/` is a numbered series of experiments:
  hello world, counters over HTMX and websockets, a todo
  CRUD app, chat against OpenAI, Mistral, Llama 3.1 and
  Claude, file upload, and a RAG chat on Milvus
  (`test04_chat_rag_milvus.py`).
- [[RAG Demo App]] is the cleaned-up result. It uses
  `hx_swap_oob` to append chat messages and a websocket
  route to stream replies.
- `demo_AI_NEWSLETTER/scrape_ui_fasthtml` is a scraper UI,
  with a Streamlit twin next to it for comparison.

Apps start with `serve()` at the end of the file, or with
`uvicorn module:app --reload`.

## Sources

- `fasthtml/README.txt`
- `demo_RAG/rag_unix/common_tools.py`
