---
type: Module
title: mychat Chatbots
description: Four minimal chatbot apps in mychat/, one per UI framework, used in Lesson 5 of the curriculum.
tags: [chatbot, demo, web]
timestamp: 2026-09-15T00:00:00Z
---

# mychat Chatbots

Four small chat apps, one per framework, so a learner can
compare how each one handles a conversation. Each folder
has a `run.sh`. They are the coding task for Lesson 5 of
the [[AI Training Curriculum]].

| Folder | UI | Model |
|---|---|---|
| `mychat/chainlit-openai/` | Chainlit | OpenAI |
| `mychat/chainlit-ollama/` | Chainlit | [[Ollama]] |
| `mychat/flask-openai/` | Flask with templates | OpenAI |
| `mychat/streamlit-openai/` | Streamlit | OpenAI |

The later chat work moved to [[FastHTML]], which led to
the [[RAG Demo App]].

## Sources

- `mychat/`
- `README.md` (Lesson 5)
