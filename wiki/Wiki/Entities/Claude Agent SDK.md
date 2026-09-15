---
type: Library
title: Claude Agent SDK
description: Anthropic's Python SDK for building agents on the Claude Code harness, configured through ClaudeAgentOptions.
tags: [claude, agents, library]
timestamp: 2026-09-15T00:00:00Z
---

# Claude Agent SDK

Anthropic's library for running Claude Code's agent loop
inside your own program (`claude_agent_sdk` in Python).
Behaviour is set with `ClaudeAgentOptions`: `cwd`,
`setting_sources`, `system_prompt`, `allowed_tools`, and
skills.

The notes in `claude_howto/` deal with one question:
keeping development configuration away from the deployed
agent. See [[Dev vs Runtime Agent Config]].

The plain Anthropic API client is separate. It appears in
`ai_tests/test5_Claude.py`,
`ai_tests/test6_Claude_stream_chat.py` and the
[[RAG Demo App]], which call `anthropic.Anthropic()` or
`AsyncAnthropic()` directly and read `ANTHROPIC_API_KEY`
from the environment.

## Sources

- `claude_howto/README.md`
- `claude_howto/dev-vs-runtime-agent-config.md`
- `ai_tests/test5_Claude.py`
