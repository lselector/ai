# Skill names use hyphens, never underscores

Skill names — both the directory under `.claude/skills/<name>/` and the `name:` field in that skill's `SKILL.md` frontmatter — must use **hyphens** for word separation, never underscores. So `/mycron-apply`, not `/mycron_apply`. Existing skills (`linkedin-prep`, `linkedin-work`, `youtube-post`, `x-post`, `gforward`, `gread`, etc.) follow this convention; the user enforces it for any new skills.

**Why:** User explicitly asked for this. Slash commands and CLI verbs read more naturally with hyphens (`/foo-bar` looks like a command; `/foo_bar` looks like a Python identifier). The user has had to ask once to fix a violation, so don't repeat.

**How to apply:**
- When creating a new skill, name the directory `<word1>-<word2>-...` and put the same hyphenated name in the `name:` frontmatter field. Never use `_`.
- When referencing an existing skill in a description, README, log, or another skill's text, write `/the-skill-name` with hyphens.
- This rule applies **only to skill names**, not to underlying Python tool files in `tools/`. Python modules can't have hyphens, so a skill `/mycron-apply` legitimately maps to `tools/mycron_apply.py`. Don't try to rename Python files to use hyphens.
- If you spot an existing skill that violates this rule, flag it for renaming rather than silently leaving it.
