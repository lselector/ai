# Separating Dev and Runtime Rules in an Agentic App

Source: `claude-agent-sdk-dev-prod-separation-thread.md`

## The problem

You use a Claude agent twice over, for two different jobs.

**Development.** You sit in VS Code or Zed with Claude Code
open, working on the app. Here you want coding rules,
testing standards, architecture notes, repo navigation
skills, dev MCP servers.

**Runtime.** The finished app runs and does business work
for a user. Here you want domain rules, approved
procedures, an output schema, a narrow set of business
tools. The coding material is noise at best. At worst it
leaks repo internals into business output.

Moving the dev material into a folder named `devrules/`
does not solve this. A folder name is not a boundary. The
Agent SDK discovers `CLAUDE.md` and `.claude/` by walking
up from its working directory whenever the matching setting
sources are enabled, so if the runtime session starts
anywhere inside the repo it finds them. And even with
discovery off, an agent holding `Read` or `Bash` can just
go read the files.

Two separate things have to be controlled:

- **What gets loaded automatically** - controlled by
  `cwd`, `setting_sources`, `system_prompt`, `skills`.
- **What can be reached at all** - controlled by the tool
  allowlist and by which files exist in the deployed
  filesystem.

Prompt and skill filtering shape behavior. Filesystem and
tool limits control access. You need both.

## The solution

Two `ClaudeAgentOptions` objects, one repo, one deployment
boundary.

| | Dev | Runtime |
|---|---|---|
| `cwd` | repo root | separate workspace outside the repo |
| `setting_sources` | `["project"]` | `[]` |
| `system_prompt` | `claude_code` preset | your own text from `runtime/` |
| Rules and skills | `.claude/` auto-loaded | `runtime/` loaded explicitly |
| Tools | Read, Edit, Bash, Skill | business MCP tools only |

### Layout

```text
myapp/
├── app/
│   ├── agent_dev.py        # Dev SDK config
│   └── agent_runtime.py    # Runtime SDK config
│
├── .claude/                # Dev only, auto-loaded
│   ├── rules/development.md
│   └── skills/python-dev/SKILL.md
│
├── runtime/                # Runtime only, loaded by code
│   ├── myapp_system_prompt.md
│   └── skills/data-load/SKILL.md
│
└── deploy/
    └── Dockerfile          # Copies app/ and runtime/
```

`/var/lib/myapp/workspace` is deliberately absent from the
tree. The deployment creates it. It holds business data and
agent output, and it never belongs in Git.

### Dev config

```python
from claude_agent_sdk import ClaudeAgentOptions

dev = ClaudeAgentOptions(
    cwd="/path/to/myapp",         # repo root
    setting_sources=["project"],  # loads .claude/
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
    },
    allowed_tools=[
        "Read", "Edit", "Bash", "Skill",
    ],
)
```

### Runtime config

```python
from claude_agent_sdk import ClaudeAgentOptions

runtime = ClaudeAgentOptions(
    cwd="/var/lib/myapp/workspace",  # not the repo
    setting_sources=[],              # no .claude/
    system_prompt="You are the MyApp runtime agent.",
    allowed_tools=["mcp__myapp__load_data"],
)
```

That is the whole idea. `setting_sources=[]` switches off
discovery of user and project settings, `CLAUDE.md` files,
and filesystem skills. Nothing from `.claude/` reaches the
running app.

## Detailed example

Runtime rules and skills stay in Git. They are reviewed
source, same as code. The difference is that Python loads
them on purpose instead of the SDK finding them by accident.

### Directory

```text
myapp/
├── app/
│   ├── main.py
│   └── agent/
│       ├── dev.py              # dev factory
│       ├── runtime.py          # runtime factory
│       └── checks.py           # startup assertions
│
├── .claude/                    # DEV ONLY
│   ├── settings.json
│   ├── rules/
│   │   ├── engineering.md
│   │   └── testing.md
│   └── skills/
│       ├── python-dev/SKILL.md
│       └── architecture-review/SKILL.md
│
├── dev/                        # DEV ONLY
│   ├── fixtures/
│   └── scripts/
│
├── runtime/                    # RUNTIME ONLY
│   ├── prompts/
│   │   └── myapp_system_prompt.md
│   ├── policies/
│   │   └── data_handling.md
│   └── plugins/
│       └── myapp_tasks/
│           ├── .claude-plugin/plugin.json
│           └── skills/
│               ├── data-load/SKILL.md
│               └── draft-report/SKILL.md
│
├── tests/
└── deploy/
    ├── Dockerfile
    └── .dockerignore
```

### app/agent/dev.py

```python
"""
Development agent configuration for MyApp.

Used when working on the code with the Agent SDK.
Loads the repo's .claude rules and skills.

Usage:
    from app.agent.dev import make_dev_options
    options = make_dev_options()

Created 2026-09-11. Updated 2026-09-11.
"""

from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions

REPO_ROOT = Path(__file__).resolve().parents[2]

DEV_APPEND = """
You are helping develop MyApp.
Follow the repository engineering and testing rules.
Keep real business data out of fixtures and logs.
"""


# --------------------------------------------------------------
def make_dev_options() -> ClaudeAgentOptions:
    """Build the SDK options used during development."""
    return ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        setting_sources=["user", "project"],
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": DEV_APPEND,
        },
        allowed_tools=[
            "Read", "Write", "Edit",
            "Glob", "Grep", "Bash", "Skill",
        ],
    )
```

Drop `"user"` from `setting_sources` if your personal
`~/.claude` config should stay out of the project.

### app/agent/runtime.py

```python
"""
Runtime agent configuration for MyApp.

Used when the shipped app does business work. Loads
nothing by discovery. Prompt and skills come from
runtime/, which is versioned in Git.

Usage:
    from app.agent.runtime import make_runtime_options
    options = make_runtime_options()

Created 2026-09-11. Updated 2026-09-11.
"""

import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions

PKG_ROOT = Path(__file__).resolve().parents[2]
PROMPT = PKG_ROOT / "runtime/prompts/myapp_system_prompt.md"
PLUGIN = PKG_ROOT / "runtime/plugins/myapp_tasks"

WORKSPACE = Path(
    os.environ.get(
        "MYAPP_WORKSPACE",
        "/var/lib/myapp/workspace",
    )
)


# --------------------------------------------------------------
def make_runtime_options() -> ClaudeAgentOptions:
    """Build the hermetic SDK options used at runtime."""
    return ClaudeAgentOptions(
        cwd=str(WORKSPACE),
        setting_sources=[],
        system_prompt=PROMPT.read_text(encoding="utf-8"),
        plugins=[
            {"type": "local", "path": str(PLUGIN)},
        ],
        skills=[
            "myapp-tasks:data-load",
            "myapp-tasks:draft-report",
        ],
        allowed_tools=[
            "Skill",
            "mcp__myapp__load_data",
            "mcp__myapp__save_report",
        ],
        env={
            "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
            "CLAUDE_CONFIG_DIR": "/var/lib/myapp/cfg",
        },
    )
```

Because `setting_sources=[]` also disables skill discovery,
runtime skills cannot arrive on their own. They come in
through the local plugin, and only the names in `skills`
can be invoked. Anything not on that list is unreachable
through the Skill tool.

### Deployment boundary

One repo does not mean one deployed tree. The image copies
`app/` and `runtime/` and leaves the dev material behind.

```text
# deploy/.dockerignore
.git/
.claude/
dev/
tests/
CLAUDE.md
.env
.env.*
__pycache__/
.venv/
```

### Startup check

Configuration drifts. Assert the boundary rather than
trusting it.

```python
# --------------------------------------------------------------
def validate_runtime(options) -> None:
    """Fail fast if runtime isolation was weakened."""
    if options.setting_sources != []:
        raise RuntimeError(
            "runtime must use setting_sources=[]"
        )

    broad = {"Read", "Write", "Edit", "Bash", "Glob", "Grep"}
    leaked = broad & set(options.allowed_tools or [])
    if leaked:
        raise RuntimeError(
            f"broad filesystem tools at runtime: {leaked}"
        )
```

## Things that bite

- A `skills` allowlist blocks invocation, not reading. An
  agent with `Bash` can still `cat` a SKILL.md.
- Mounting the repo into the runtime container undoes the
  Dockerfile boundary. Check your compose file.
- Rules that really matter belong in the versioned runtime
  prompt or, better, in deterministic Python and MCP tools
  that validate their own inputs. A prompt is guidance. A
  tool signature is enforcement.
- Never commit secrets, tokens, or real business documents
  to `runtime/`. Those go to environment variables, a
  secret manager, or an approved data store.

Reference: https://code.claude.com/docs/en/agent-sdk/skills
