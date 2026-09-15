---
type: Pattern
title: Dev vs Runtime Agent Config
description: Keep Claude Code development rules and skills out of a running Agent SDK app with separate cwd, setting_sources and tool lists.
tags: [claude-agent-sdk, security, pattern]
timestamp: 2026-09-15T00:00:00Z
---

# Dev vs Runtime Agent Config

An app built with the [[Claude Agent SDK]] meets an agent
twice: Claude Code while you develop it, and the app's own
agent while it serves users. Coding rules must not leak
into the business agent. The fix is two separate
`ClaudeAgentOptions` objects.

## Why a folder name is not enough

The SDK finds `CLAUDE.md` and `.claude/` by walking up
from its working directory whenever setting sources are
on. A runtime session started anywhere inside the repo
picks them up. And an agent with `Read` or `Bash` can open
the files even with discovery off. Two things need
control:

- what loads automatically: `cwd`, `setting_sources`,
  `system_prompt`, `skills`;
- what can be reached at all: the tool allowlist and the
  files present in the deployed filesystem.

## The two configs

| | Dev | Runtime |
|---|---|---|
| `cwd` | repo root | workspace outside the repo |
| `setting_sources` | `["project"]` | `[]` |
| `system_prompt` | `claude_code` preset | app's own prompt |
| Rules and skills | `.claude/`, auto-loaded | `runtime/`, loaded by code |
| Tools | Read, Edit, Bash, Skill | business MCP tools only |

`setting_sources=[]` turns off discovery of settings,
`CLAUDE.md` files and filesystem skills. Runtime prompts
still live in git under `runtime/`; Python loads them on
purpose. The Docker image copies only `app/` and
`runtime/`.

## Sources

- `claude_howto/dev-vs-runtime-agent-config.md`
- `claude_howto/claude-agent-sdk-dev-prod-separation-thread.md`
