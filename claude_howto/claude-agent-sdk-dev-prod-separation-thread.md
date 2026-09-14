# Claude Agent SDK: Separating Development and Runtime Rules

## User

I have a personal agent on my computer. It is written in python using claude-agent-sdk module. Its purpose - business tasks related to SOX audit. When I am working with it, there are two situations:
(1) I am developing the app in VS Code or Zed using Claude Code
(2) I am running the agent to do business tasks.

I have rules and skills which I want to use during development, and a different rules and skills which I use during running the application.

How to cleanly separate those rules and skills?
I tried to put dev rules into a separate directory called "devrules" - but Claude still finds and loads these rules even when I am running the app and not doing development

## Assistant

You should treat **development** and **runtime SOX work** as two distinct agent configurations—not merely two folders of Markdown. The clean boundary is set in the Python `ClaudeAgentOptions`: use different `cwd`, `setting_sources`, `skills`, system prompt, tools, MCP servers, and permissions for each mode.

Your `devrules/` directory does not create an isolation boundary. If runtime sessions use the repository root as `cwd`, enable the `project` source, allow broad filesystem access, or use a Claude Code preset that provides repository context, Claude can still read those files. Also, any `CLAUDE.md` under the runtime working directory or its parents is injected as project context when the relevant setting source is enabled.

## Recommended model

Split the system into three layers:

| Layer | Development mode | Runtime SOX mode |
|---|---|---|
| System instructions | Coding conventions, architecture, tests, review standards | SOX role, evidence handling, audit workflow, output schema, approval gates |
| Skills | `pytest`, migration, code review, deployment, repo navigation | Evidence collection, control testing, PBC requests, workpaper drafting, issue triage |
| Tools and access | Filesystem, Git, shell, test runner, local environment | Narrow approved business tools and data sources; ideally no arbitrary shell or repo write access |
| Filesystem context | Application repository | A separate runtime workspace/data directory |
| SDK settings | `setting_sources=["user", "project"]` where appropriate | Usually `setting_sources=[]` and an explicit skill allowlist |
| Prompt base | `claude_code` preset + dev instructions | Custom non-coding system prompt |

For a SOX agent, avoid using the `claude_code` preset at runtime unless the agent truly needs to behave like an interactive coding tool. A custom system prompt is generally more appropriate for a non-coding, domain-specific, or differently permissioned agent.

## Make runtime hermetic

The key change is: **do not let production/runtime sessions discover project or personal Claude configuration by default.**

```python
from claude_agent_sdk import ClaudeAgentOptions, query

RUNTIME_SYSTEM_PROMPT = """
You are an internal SOX audit-support agent.

Scope:
- Assist with authorized SOX compliance and audit-support tasks only.
- Work only with evidence and data supplied through approved tools or the
  designated runtime workspace.
- Do not inspect, modify, or rely on application source code, development
  instructions, local developer notes, Git history, or unrelated files.

Evidence discipline:
- Clearly distinguish source evidence, assumptions, missing evidence, and conclusions.
- Preserve citations, source identifiers, dates, owners, and review status.
- Do not fabricate evidence, control performance, approvals, or test results.
- Escalate contradictions, missing evidence, and potentially material control issues.
- Return structured output suitable for reviewer sign-off.
"""

runtime_options = ClaudeAgentOptions(
    # Crucial: not the repo root.
    cwd="/srv/sox-agent/runtime-workspace",

    # Prevent SDK discovery/loading of:
    # ~/.claude/CLAUDE.md, ~/.claude/skills,
    # repo CLAUDE.md, repo .claude/skills, etc.
    setting_sources=[],

    # No discovered filesystem skills.
    skills=[],

    # A business-agent prompt, not a coding-agent prompt.
    system_prompt=RUNTIME_SYSTEM_PROMPT,

    # Keep this narrow and specific to your business workflow.
    allowed_tools=[
        "mcp__sox_evidence__search",
        "mcp__sox_evidence__get_document",
        "mcp__gdrive__search",
        "mcp__gdrive__fetch",
    ],
)

async for message in query(
    prompt="Assess the evidence for control ITGC-AC-012 for Q3.",
    options=runtime_options,
):
    print(message)
```

With `setting_sources=[]`, the SDK does not load user or project `CLAUDE.md` files or filesystem-discovered skills. Skills are discovered through the `user` and `project` setting sources; if those sources are omitted, they are not loaded.

## Package runtime skills explicitly

Filesystem skills are ordinarily discovered through `setting_sources`. Do not enable the whole project source just to make runtime skills available, because it can bring back project `CLAUDE.md`, project skills, and other configuration.

Use one of these patterns.

### Option A: Put SOX procedures in the runtime system prompt

Best for compact, stable rules:

- Evidence integrity and non-fabrication.
- Required audit conclusion schema.
- Materiality and escalation boundaries.
- Privacy and confidentiality instructions.
- “No action without approval” policy.
- Authoritative data systems.

### Option B: Load approved SOX skills via a dedicated plugin

Best for reusable, larger task procedures. Keep the artifacts out of the application repository’s normal `.claude/skills/` discovery path.

```text
sox-agent/
├── app/
│   ├── main.py
│   └── agent/
│       ├── runtime.py
│       └── dev.py
├── runtime-workspace/
│   ├── incoming/
│   ├── normalized/
│   └── outputs/
└── sox-runtime-plugin/
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
        ├── evaluate-control-evidence/
        │   └── SKILL.md
        ├── draft-workpaper/
        │   └── SKILL.md
        ├── identify-evidence-gaps/
        │   └── SKILL.md
        └── create-pbc-request/
            └── SKILL.md
```

Conceptually:

```python
runtime_options = ClaudeAgentOptions(
    cwd="/srv/sox-agent/runtime-workspace",
    setting_sources=[],
    plugins=[
        {
            "type": "local",
            "path": "/srv/sox-agent/sox-runtime-plugin",
        }
    ],
    skills=[
        "sox-runtime:evaluate-control-evidence",
        "sox-runtime:draft-workpaper",
        "sox-runtime:identify-evidence-gaps",
        "sox-runtime:create-pbc-request",
    ],
    system_prompt=RUNTIME_SYSTEM_PROMPT,
    allowed_tools=[
        "Skill",
        "mcp__sox_evidence__search",
        "mcp__sox_evidence__get_document",
    ],
)
```

### Option C: Implement SOX “skills” as Python task modules

For regulated workflows, expose deterministic Python tools such as:

- `get_control(control_id)`
- `list_required_evidence(control_id, period)`
- `search_evidence(control_id, period, query)`
- `validate_evidence_metadata(document_id)`
- `create_draft_workpaper(control_id, test_id, findings)`
- `submit_for_reviewer_approval(workpaper_id)`

The LLM performs reasoning and narrative synthesis; Python enforces tenant and engagement boundaries, required schemas, audit logs, evidence hashes, human approvals, and allowed control IDs, periods, and data sources.

## Keep development separate

Use a separate development configuration:

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

REPO_ROOT = Path(__file__).resolve().parents[2]

DEV_SYSTEM_APPEND = """
You are assisting with development of the SOX audit-support agent.

Follow the repository architecture and engineering conventions.
Prioritize:
- Typed Python and clear module boundaries
- Tests for audit-critical transformations
- Schema validation and provenance preservation
- Least-privilege tool design
- Immutable logging and reviewer approval workflows
- Avoiding exposure of sensitive business evidence in fixtures or logs
"""

dev_options = ClaudeAgentOptions(
    cwd=str(REPO_ROOT),
    setting_sources=["user", "project"],
    system_prompt={
        "type": "preset",
        "preset": "claude_code",
        "append": DEV_SYSTEM_APPEND,
    },
    allowed_tools=[
        "Read",
        "Write",
        "Edit",
        "Grep",
        "Glob",
        "Bash",
        "Skill",
    ],
)
```

## Move development content out of runtime reach

Do not place development rules in a generic repository directory and assume the runtime agent cannot read them. If the runtime agent has `Read`, `Bash`, or a permissive filesystem sandbox, it can find them regardless of automatic injection.

Use separate deployment filesystems or container images:

```text
~/work/sox-agent-dev/                 # Developer checkout
├── CLAUDE.md                         # Development-only instructions
├── .claude/
│   ├── skills/                       # Development-only skills
│   └── rules/                        # Development-only rules
├── dev/
│   ├── prompts/
│   └── fixtures/
└── app/

~/sox-agent-runtime/                  # Runtime deployment or container filesystem
├── app/
├── runtime-workspace/
├── runtime-config/
│   ├── system-prompt.md
│   └── policies/
└── sox-runtime-plugin/
```

In production, exclude `.claude/`, `CLAUDE.md`, `devrules/`, test fixtures, source-control metadata when unnecessary, editor configuration, local notes, and developer credentials.

## Important caveat

A `skills=[...]` allowlist prevents invocation of unlisted skills through the Skill mechanism, but it does not prevent the model from reading skill files if it still has broad `Read` or `Bash` access to a filesystem containing them.

> Prompt and skill filtering control behavior; filesystem and tool boundaries control access. Use both.

## Practical recommendation

1. Keep `.claude/`, `CLAUDE.md`, developer skills, and development rules only in the development checkout.
2. Create `make_dev_options()` using `cwd=repo_root`, project/user setting sources, a Claude Code preset, and a development-skill allowlist.
3. Create `make_runtime_options()` using a separate runtime `cwd`, `setting_sources=[]`, a custom SOX system prompt, and a narrow tool allowlist.
4. Put critical SOX policy into versioned prompt files and deterministic Python/MCP tools.
5. Run the runtime agent in a separate container or process profile without the developer checkout, `.claude` directories, home directory, Git metadata, or arbitrary shell access.
6. Inspect and assert the initialized skill list in CI and at runtime startup.

---

## User

Please make a short 100-120 words plain text (no markup, no link references) summary as bulleted list. Start with title (20-40 chars), followed by the list, followed by the main relevany URL

## Assistant

Separating Dev and SOX Runtime

- Use two explicit Claude Agent SDK configurations rather than relying on folders.
- Development mode can use the repository root, project/user setting sources, Claude Code preset, and developer skills.
- Runtime mode should use a separate working directory, a custom SOX-focused system prompt, setting_sources=[], and an explicit tool allowlist.
- Keep runtime skill procedures in an approved plugin or expose critical workflows as deterministic Python/MCP tools.
- Do not deploy CLAUDE.md, .claude, devrules, test fixtures, Git metadata, or developer home directories into the runtime environment.
- A skill allowlist does not stop access through broad Read or Bash tools; enforce filesystem isolation and least-privilege permissions.
- Log effective configuration and assert discovered runtime skills at startup.

https://code.claude.com/docs/en/agent-sdk/skills

---

## User

Can I have both Prod and Dev saved in the same Github repo? How directories will be organized? How the runtime settings will be done in Python?

## Assistant

Yes. Keep both in one GitHub repository, but make the **runtime process explicitly isolated**. The directory layout is for maintainability; the actual safety boundary comes from `cwd`, `setting_sources=[]`, an explicit tool list, and a deployment image that excludes development-only files.

## Suggested repository layout

```text
sox-audit-agent/
├── README.md
├── pyproject.toml
├── .gitignore
├── .dockerignore
├── .env.example
│
├── app/                              # Runtime application code
│   ├── __init__.py
│   ├── main.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── runtime.py                # Runtime agent factory
│   │   ├── dev.py                    # Development agent factory
│   │   ├── prompts.py                # Reads versioned prompt files
│   │   ├── tools.py                  # Deterministic Python tools
│   │   └── policies.py               # Input/output validation
│   │
│   ├── domain/
│   │   ├── controls.py
│   │   ├── evidence.py
│   │   ├── workpapers.py
│   │   └── audit_log.py
│   │
│   └── api/
│       └── server.py
│
├── runtime/                          # Runtime-only policy/config artifacts
│   ├── prompts/
│   │   └── sox_system_prompt.md
│   ├── schemas/
│   │   ├── evidence_assessment.json
│   │   ├── workpaper_draft.json
│   │   └── pbc_request.json
│   ├── policies/
│   │   ├── evidence_handling.md
│   │   └── escalation_policy.md
│   └── plugins/
│       └── sox_audit/
│           ├── .claude-plugin/
│           │   └── plugin.json
│           └── skills/
│               ├── evaluate-control-evidence/
│               │   └── SKILL.md
│               ├── draft-workpaper/
│               │   └── SKILL.md
│               └── identify-evidence-gaps/
│                   └── SKILL.md
│
├── dev/                              # Development-only material
│   ├── prompts/
│   │   └── developer_instructions.md
│   ├── fixtures/
│   ├── scripts/
│   └── architecture/
│       └── decisions.md
│
├── .claude/                          # Used only by Claude Code during development
│   ├── settings.json
│   ├── rules/
│   │   ├── engineering.md
│   │   ├── testing.md
│   │   └── security-review.md
│   └── skills/
│       ├── python-engineering/
│       │   └── SKILL.md
│       ├── test-sox-workflow/
│       │   └── SKILL.md
│       └── architecture-review/
│           └── SKILL.md
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── security/
│
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── kubernetes/
│
└── docs/
    ├── architecture.md
    └── threat-model.md
```

This works because developer use of Claude Code intentionally runs from the repository root, where `.claude/` and root-level `CLAUDE.md` are available. The business runtime runs from a separate runtime workspace and disables filesystem settings discovery.

## Development configuration

```python
# app/agent/dev.py
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions

REPO_ROOT = Path(__file__).resolve().parents[2]

DEV_PROMPT = """
You are helping develop a SOX audit-support application.

Follow the repository's engineering instructions, testing standards,
security requirements, architecture conventions, and data-handling rules.

Priorities:
- Preserve auditability and provenance.
- Use typed, validated Python interfaces.
- Test business-critical transformations.
- Do not place real audit evidence in fixtures, logs, or commits.
"""

def make_dev_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        setting_sources=["user", "project"],
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": DEV_PROMPT,
        },
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Glob",
            "Grep",
            "Bash",
            "Skill",
        ],
    )
```

## Runtime configuration

The runtime configuration should never use the repository root as its working directory.

```python
# app/agent/runtime.py
import os
from pathlib import Path

from claude_agent_sdk import ClaudeAgentOptions

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
RUNTIME_WORKSPACE = Path(
    os.environ.get("SOX_RUNTIME_WORKSPACE", "/var/lib/sox-agent/workspace")
)
RUNTIME_PROMPT = PACKAGE_ROOT / "runtime/prompts/sox_system_prompt.md"
RUNTIME_PLUGIN = PACKAGE_ROOT / "runtime/plugins/sox_audit"

def read_runtime_prompt() -> str:
    return RUNTIME_PROMPT.read_text(encoding="utf-8")

def make_runtime_options() -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        cwd=str(RUNTIME_WORKSPACE),
        setting_sources=[],
        system_prompt=read_runtime_prompt(),
        plugins=[
            {
                "type": "local",
                "path": str(RUNTIME_PLUGIN),
            }
        ],
        skills=[
            "sox-audit:evaluate-control-evidence",
            "sox-audit:draft-workpaper",
            "sox-audit:identify-evidence-gaps",
        ],
        allowed_tools=[
            "Skill",
            "mcp__sox_evidence__search",
            "mcp__sox_evidence__get_document",
            "mcp__sox_workpapers__create_draft",
            "mcp__sox_workpapers__get_template",
        ],
        env={
            "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1",
            "CLAUDE_CONFIG_DIR": "/var/lib/sox-agent/claude-config",
        },
    )
```

## Runtime prompt example

Keep this prompt in `runtime/prompts/sox_system_prompt.md`, version it in Git, and require code review for changes.

```text
You are a SOX audit-support agent operating within an approved business workflow.

Scope:
- Help assess evidence, draft workpapers, identify evidence gaps, and prepare
  reviewer-ready SOX documentation.
- Use only approved tools and explicitly supplied data.
- Do not inspect software source code, developer instructions, local notes,
  Git history, personal directories, or unrelated files.

Evidence requirements:
- Treat retrieved evidence as source material; preserve document IDs, timestamps,
  source systems, owners, and retrieval dates.
- Never invent evidence, execution, approvals, reviewer sign-off, or conclusions.
- Distinguish facts, assumptions, missing evidence, and recommendations.
- Flag conflicts, stale evidence, incomplete populations, and exceptions.

Output:
- Produce structured, reviewer-ready outputs.
- Include evidence references and a confidence/limitations section.
- Mark all workpapers as drafts pending human reviewer approval.

Safety:
- Do not send communications, modify records, or finalize workpapers without
  the relevant authorized workflow and explicit reviewer approval.
```

Python tools should enforce important controls rather than relying only on the prompt. For example, a `create_workpaper_draft()` tool can require a control ID, period, engagement ID, evidence IDs, and `status="draft"`; it should refuse “final” status without a reviewer authorization token.

## Docker deployment boundary

Using one repository does not mean deploying the entire repository. A Docker image can copy only application and runtime artifacts.

```dockerfile
# deploy/Dockerfile
FROM python:3.12-slim

WORKDIR /opt/sox-agent

RUN useradd --create-home --uid 10001 agentuser

COPY pyproject.toml ./
COPY app ./app
COPY runtime ./runtime

RUN pip install --no-cache-dir .

RUN mkdir -p /var/lib/sox-agent/workspace \
    /var/lib/sox-agent/claude-config \
    && chown -R agentuser:agentuser /opt/sox-agent /var/lib/sox-agent

USER agentuser

ENV SOX_RUNTIME_WORKSPACE=/var/lib/sox-agent/workspace
ENV CLAUDE_CODE_DISABLE_AUTO_MEMORY=1
ENV CLAUDE_CONFIG_DIR=/var/lib/sox-agent/claude-config

CMD ["python", "-m", "app.main"]
```

Example `.dockerignore`:

```text
.git/
.github/
.claude/
dev/
tests/
docs/
README.md
CLAUDE.md
.env
.env.*
__pycache__/
.pytest_cache/
.venv/
```

## Validate isolation at startup

```python
# app/agent/runtime_checks.py
from pathlib import Path

def validate_runtime_environment(options) -> None:
    cwd = Path(options.cwd).resolve()

    if cwd.name != "workspace":
        raise RuntimeError(f"Runtime cwd must be the workspace, got: {cwd}")

    if options.setting_sources != []:
        raise RuntimeError(
            "Runtime must use setting_sources=[] to prevent loading "
            "developer and filesystem Claude configuration."
        )

    forbidden = {"Read", "Write", "Edit", "Bash", "Glob", "Grep"}
    configured = set(options.allowed_tools or [])
    unexpected = forbidden & configured

    if unexpected:
        raise RuntimeError(
            f"Runtime includes forbidden broad filesystem tools: {sorted(unexpected)}"
        )
```

## Bottom line

Use **one repo, two configurations, and one production build boundary**:

- `.claude/` and `dev/` are committed for developers and Claude Code.
- `runtime/` contains production prompts, schemas, policies, and approved SOX skills.
- Runtime Python uses a non-repository `cwd`, `setting_sources=[]`, a custom system prompt, explicitly loaded runtime plugins/skills, and narrow business-only tools.
- The production Docker image copies `app/` and `runtime/`, not `.claude/` or `dev/`.

---

## User

Please make a much shorter example of Suggested repository layout. Remove most of stuff. Just demonstrate how the rules and skills are separated between dev and prod

## Assistant

SOX Agent: Dev vs Prod Layout

```text
sox-audit-agent/
├── app/
│   ├── agent_dev.py             # Dev SDK configuration
│   └── agent_runtime.py         # Production SDK configuration
│
├── .claude/                     # Development only: loaded by Claude Code
│   ├── rules/
│   │   └── development.md
│   └── skills/
│       └── python-dev/
│           └── SKILL.md
│
├── runtime/                     # Production only: explicitly loaded by app
│   ├── sox_system_prompt.md
│   └── skills/
│       └── audit-evidence/
│           └── SKILL.md
│
└── deploy/
    └── Dockerfile               # Copies app/ and runtime/, excludes .claude/
```

Development runs from the repository root with project settings enabled, so Claude Code loads `.claude/rules` and `.claude/skills`.

Production runs from a separate workspace with `setting_sources=[]`, so it does not discover `.claude` rules or skills. The Python application loads only `runtime/sox_system_prompt.md` and explicitly approved production skills.

https://code.claude.com/docs/en/agent-sdk/skills

---

## User

please give a very-very-very short example of Runtime configuration in python

## Assistant

```python
from claude_agent_sdk import ClaudeAgentOptions

runtime = ClaudeAgentOptions(
    cwd="/var/sox/workspace",
    setting_sources=[],          # Do not load .claude or CLAUDE.md
    system_prompt="You are a SOX audit-support agent.",
    allowed_tools=["mcp__sox__search_evidence"],
)
```

Use a runtime workspace outside the Git repository. `setting_sources=[]` prevents automatic loading of development rules and skills.

---

## User

what is cwd ?

## Assistant

`cwd` means **current working directory**: the folder from which the agent process operates.

In this configuration:

```python
cwd="/var/sox/workspace"
```

it tells the Claude Agent SDK to treat `/var/sox/workspace` as its working folder. Relative file paths, shell commands, and project-related discovery begin there.

For the separation:

- Dev: `cwd="/path/to/sox-audit-agent"` — the Git repository, where `.claude/` development rules and skills exist.
- Prod: `cwd="/var/sox/workspace"` — a separate business-data workspace, not the repository.

Use `cwd` together with `setting_sources=[]` in production. `cwd` alone does not prevent access to repository files if broad tools are provided or the repository is mounted into the runtime environment.

---

## User

give similar short example of dev python config

## Assistant

```python
from claude_agent_sdk import ClaudeAgentOptions

dev = ClaudeAgentOptions(
    cwd="/path/to/sox-audit-agent",      # Git repository
    setting_sources=["project"],          # Load .claude and CLAUDE.md
    system_prompt="You are helping develop this SOX agent.",
    allowed_tools=["Read", "Edit", "Bash", "Skill"],
)
```

`cwd` is the repository folder, and `setting_sources=["project"]` enables its Claude Code development rules and skills. Use `"user"` too only if personal `~/.claude` configuration should also load.

---

## User

[Attached slide image]

Attached slide demonstrates the directory layout, and dev and prod configs. I wanted to make it generic (myapp instead of SOX, ...). Please suggest changes to make the three boxes consistent. For example, the "cwd" paths in python should correspond to actual paths in the directory structure

## Assistant

The main inconsistency is that the tree says `sox-audit-agent/`, while the code uses generic `myapp` paths, and the dev prompt still refers to a “myapp agent.” Make the repository name, `cwd` values, prompt names, runtime skill name, and Docker comment all use the same generic application name.

## Suggested revised slide text

### Directories

```text
# Directories
myapp/
├── app/
│   ├── agent_dev.py          # Dev SDK configuration
│   └── agent_runtime.py      # Runtime SDK configuration
│
├── .claude/                  # Dev only: loaded by Claude Code
│   ├── rules/development.md
│   └── skills/python-dev/SKILL.md
│
├── runtime/                  # Runtime only: explicitly loaded by app
│   ├── myapp_system_prompt.md
│   └── skills/data-load/SKILL.md
│
└── deploy/
    └── Dockerfile            # Copies app/ and runtime/, excludes .claude/
```

### Dev config

```python
from claude_agent_sdk import ClaudeAgentOptions

dev = ClaudeAgentOptions(
    cwd="/path/to/myapp",             # Repository root: myapp/
    setting_sources=["project"],      # Load myapp/.claude and CLAUDE.md
    system_prompt="You are helping develop MyApp.",
    allowed_tools=["Read", "Edit", "Bash", "Skill"],
)
```

### Runtime config

```python
from claude_agent_sdk import ClaudeAgentOptions

runtime = ClaudeAgentOptions(
    cwd="/var/lib/myapp/workspace",   # Separate runtime workspace
    setting_sources=[],               # Do not load .claude or CLAUDE.md
    system_prompt="You are the MyApp runtime agent.",
    allowed_tools=["mcp__myapp__load_data"],
)
```

## Key consistency changes

- Rename top-level `sox-audit-agent/` to `myapp/`.
- Make dev `cwd` point to the directory shown in the tree: `/path/to/myapp`.
- Make runtime `cwd` visibly separate from the repository: `/var/lib/myapp/workspace`.
- Rename `sox_system_prompt.md` to `myapp_system_prompt.md`.
- Use the same product name in both system prompts: `MyApp`.
- Replace `mcp__myapp_load_data` with the more conventional namespaced style `mcp__myapp__load_data`.
- Change “Production SDK configuration” to “Runtime SDK configuration” if it should exactly match the `runtime/` directory and the “Runtime config” box.

One subtle point: `/var/lib/myapp/workspace` is intentionally not shown under `myapp/` in the Git repository tree because it should be created by the deployment environment or Docker container, not committed to Git. This keeps business data and runtime output separate from source code.

---

## User

Can I keep the runtime rules, skills, etc in the repo?

## Assistant

Yes. You can—and usually should—keep versioned **runtime rules, prompts, skills, schemas, and policies** in the same GitHub repository as the application.

The important distinction is:

- Repository files are version-controlled source artifacts.
- The agent’s `cwd` is its operational working directory.
- `setting_sources=[]` stops automatic loading of development `.claude` configuration.
- Python explicitly loads only the runtime artifacts you approve.

## Simple layout

```text
myapp/
├── app/
│   ├── agent_dev.py
│   └── agent_runtime.py
│
├── .claude/                         # Dev only: auto-loaded in dev
│   ├── rules/development.md
│   └── skills/python-dev/SKILL.md
│
├── runtime/                         # Prod rules and skills: stored in Git
│   ├── myapp_system_prompt.md
│   ├── rules/
│   │   └── data-handling.md
│   └── skills/
│       └── data-load/SKILL.md
│
└── deploy/
    └── Dockerfile
```

## Runtime Python

```python
from pathlib import Path
from claude_agent_sdk import ClaudeAgentOptions

REPO = Path(__file__).resolve().parents[1]

runtime = ClaudeAgentOptions(
    cwd="/var/lib/myapp/workspace",  # Not the repository
    setting_sources=[],              # Do not auto-load .claude or CLAUDE.md
    system_prompt=(REPO / "runtime/myapp_system_prompt.md").read_text(),
    allowed_tools=["mcp__myapp__load_data"],
)
```

This keeps the runtime prompt in Git, while preventing automatic discovery of the development `.claude/` rules and skills. `setting_sources=[]` disables user, project, and local settings loading in the Agent SDK.

## Runtime skills

If runtime skills are implemented as `SKILL.md` files, do **not** expect the code above to load them automatically: with `setting_sources=[]`, filesystem skill discovery is disabled too. That is intentional.

Use one of these approaches:

1. Keep short/critical runtime rules in `myapp_system_prompt.md`.
2. Package `runtime/skills/` as an explicit local SDK plugin, then allowlist its skills.
3. Prefer Python/MCP tools for actions and validations that must be deterministic or auditable.

For example, a local plugin can live in the same repository under `runtime/`, but is loaded deliberately by the runtime Python configuration—not through `.claude` discovery.

## Deployment note

The production Docker image may copy both `app/` and `runtime/`, while excluding `.claude/`, `dev/`, tests, and Git metadata. Thus, runtime artifacts remain reviewed and versioned alongside code, but development-only instructions are absent from the deployed image.

Do not commit secrets, production evidence, API tokens, customer documents, or actual audit workpapers. Put those in environment variables, a secret manager, and approved runtime data stores instead.
