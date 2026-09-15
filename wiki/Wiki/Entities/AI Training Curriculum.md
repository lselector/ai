---
type: Curriculum
title: AI Training Curriculum
description: The lesson plan in the root README that walks a learner from transformer basics to local RAG.
tags: [curriculum, training]
timestamp: 2026-09-15T00:00:00Z
---

# AI Training Curriculum

The root `README.md` is a self-study course on LLMs,
chatbots and RAG. It was started in August 2023 and last
revised in May 2024, so hardware prices and links in it
date from then.

## Lessons

1. Generative AI basics: transformers, GANs, diffusion.
2. Recent AI updates (videos), plus an intro to
   [[Retrieval Augmented Generation]].
3. Running models locally with [[Ollama]] and LM Studio.
4. LangChain.
5. Simple chatbots, see [[mychat Chatbots]].
6. Moving from ChromaDB to PostgreSQL with `pgvector`.
7. A local embedding model picked from the MTEB
   leaderboard.
8. A local LLM, so the whole stack runs offline.
9. A natural-language interface to an API.
10. Language-to-report: a notebook that turns a request
    into charts.
11. and 12. Fine-tuning and training (headings only, no
    content yet).

The later hands-on work, the [[RAG Demo App]], went a
different way from lessons 6 to 8. It uses FAISS,
ChromaDB or Milvus instead of PostgreSQL, and as of
2026-09 it calls Claude instead of a local model.

## Prerequisites

The course assumes a Unix machine: Linux with an Nvidia
GPU, WSL2, or an Apple Silicon Mac with 16 GB or more.

## Sources

- `README.md`
- `2023-06-21-AI-Training.pptx`, `AI-tools-cheatsheet.pptx`
