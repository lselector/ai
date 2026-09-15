---
type: Tool
title: Ollama
description: Runs open LLMs locally from the command line; used in the curriculum and the earlier chat and RAG demos.
tags: [llm, local, tool]
website: https://ollama.ai
timestamp: 2026-09-15T00:00:00Z
---

# Ollama

A local runtime for open-weight LLMs. `ollama run
llama3:latest` downloads a model and opens a chat in the
terminal. It also serves an HTTP API that Python code
calls through the `ollama` package.

## In this repo

- Lesson 3 of the [[AI Training Curriculum]] starts
  with it.
- `ai_tests/test1_ollama.py` and
  `test2_ollama_stream.py` are the smallest examples;
  `ai_tests/howto_ollama.txt` has setup notes.
- `bin/update_ollama_mac.bash` and
  `update_ollama_linux.bash` upgrade it.
- `mychat/chainlit-ollama/` is a chat UI on it, see
  [[mychat Chatbots]].
- The [[RAG Demo App]] used it until it switched to
  Claude. Its start scripts still check `OLLAMA_MODEL`.

## Sources

- `README.md` (Lesson 3)
- `ai_tests/`, `bin/`
- `demo_RAG/rag_unix/rag_faiss_orig.py`
