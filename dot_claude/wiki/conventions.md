# Project wiki conventions

The single reference for how a project wiki is laid out
and how its pages are written. The rule
`~/.claude/rules/update_wiki.md` says when to use the
wiki; the skills `/wiki-init`, `/wiki-update` and
`/wiki-serve` say how. This file says what a correct
wiki looks like.

## What the wiki is for

The wiki is the project's long-term memory. It holds
knowledge that is expensive to rediscover and not
obvious from the code:

- why things are the way they are (decisions, rejected
  options, trade-offs);
- domain concepts and vocabulary;
- how the parts fit together (modules, services, data
  flows, external systems);
- quirks, gotchas and debugging findings;
- research: summaries of papers, vendor docs, specs,
  meeting notes, transcripts.

It is not a copy of the code, a changelog of commits,
or install instructions. Those live in the code, in git
history and in `README.md`. Claude's own memory files
hold facts about the user and how to work with them;
the wiki holds facts about the project, and it travels
with the repo.

**Never put secrets in the wiki.** No passwords, API
keys, tokens, private URLs with credentials, or
personal data. The wiki is committed to git.

## Layout

```text
wiki/
├── README.md          what this folder is (for GitHub readers)
├── Inbox/             unsorted notes waiting to be filed
├── Raw/               immutable sources, any format
│   ├── sources.md     registry: file, origin, date, notes
│   └── 01_topic/      optional numbered category folders
├── Wiki/
│   ├── Concepts/      one page per idea
│   ├── Entities/      one page per concrete thing
│   └── Summaries/     one page per Raw source
└── Dashboards/
    ├── Index.md       generated list of every page
    ├── Log.md         dated change history
    ├── Topics.md      the topic plan and keywords
    └── Home.md        optional front page of the web UI
```

Folders inside `Wiki/` stay flat: no subfolders. Links,
not folders, express relationships.

| Folder | Put here | Examples |
|---|---|---|
| `Inbox/` | Quick captures to process later | pasted chat, rough notes |
| `Raw/` | Source material, kept verbatim | PDF spec, saved web page, transcript |
| `Wiki/Summaries/` | What one source says, no opinions | `stripe-webhooks-docs.md` |
| `Wiki/Concepts/` | Ideas, decisions, patterns, domain terms | `Idempotent Webhooks.md`, `Decision - SQLite over Postgres.md` |
| `Wiki/Entities/` | Things with a name | `Billing Service.md`, `Stripe.md`, `orders Table.md` |
| `Dashboards/` | Overviews that span many pages | `Index.md`, `Architecture.md`, `Decisions.md` |

## Page names

- A page's name is its file name without `.md`. Names
  are unique across the whole wiki; `check` reports
  duplicates.
- Concepts, Entities and Dashboards use Title Case with
  spaces: `Envelope Encryption.md`.
- Summaries use the kebab-case stem of their Raw file:
  `Raw/02_apis/stripe-webhooks-docs.html` gets
  `Wiki/Summaries/stripe-webhooks-docs.md`.
- No `/`, `|`, `#`, `[` or `]` in a name.

## Page format (OKF)

Pages follow Google's Open Knowledge Format v0.1: YAML
frontmatter plus a Markdown body.
Spec: <https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md>

```markdown
---
type: Concept
title: Idempotent Webhooks
description: Handle each Stripe event once, even when it is delivered twice.
tags: [billing, reliability]
timestamp: 2026-09-15T00:00:00Z
---

# Idempotent Webhooks

Stripe retries a webhook until it gets a 2xx, so the
same event can arrive more than once. The handler in
`src/billing/webhooks.py` records each event id in the
`processed_events` table and skips ids it has seen.

## Why

Double-charging refunds happened twice in March 2026
before this was added. See [[Billing Service]].

## Sources

- [[stripe-webhooks-docs]]
- `src/billing/webhooks.py`
```

Frontmatter rules:

- `type` is required on every page except the reserved
  `Index.md` and `Log.md`. Free text. Common values:
  `Concept`, `Decision`, `Pattern`, `Entity`, `Module`,
  `Service`, `Table`, `Vendor`, `Summary`, `Dashboard`.
- Recommended: `title`, `description` (one sentence; it
  appears in the Index and section listings), `tags`,
  `timestamp`.
- Summaries add `source_file: Raw/<path>` (the web UI
  links it, and `check` uses it to find unsummarised
  sources) and `resource: <original URL>` when there is
  one.
- Optional: `resource`, `wikipedia`, `website` (any URL
  value renders as an outside link).
- One key per line. Lists as `[a, b]` or as `- item`
  lines. Quote values that contain `: ` or start with a
  special character. Never put `---` alone on a line
  inside frontmatter.

Body rules:

- Start with `# Title`, then one to three sentences
  that say what the thing is. Someone who reads only
  that should know whether they need the rest.
- Keep pages short and focused on one subject. Split a
  page that covers two.
- Point at code with repo-relative paths in backticks,
  like `src/billing/webhooks.py`.
- Date facts that will age: "as of 2026-09".
- End interpretive pages with `## Sources`: summaries,
  code paths, issues, or people's names.
- Write the prose per the humanize skill.

## Links

- Link with `[[Page Name]]` or `[[Page Name|shown text]]`.
  Plain Markdown links to `.md` files also work in the
  web UI.
- Never wrap a `[[link]]` across two lines.
- Link the first mention of every page that exists.
- Links go both ways: when page A starts linking to B,
  open B and add the link back if it helps a reader of
  B (the "ripple update").
- A link to a page that does not exist yet is allowed
  (OKF tolerates it; the UI shows it in red), but
  `check` lists it. Either write the page or remove the
  link before finishing.

## Raw sources

- Files in `Raw/` are never edited. Re-derive pages
  from them instead.
- Every new file gets a row in `Raw/sources.md`: file,
  origin URL or author, date added, notes.
- Delete a Raw file only when it must be purged (legal
  or privacy) and say why in the log.
- Large or third-party copyrighted captures may be
  gitignored; keep `sources.md` committed so they can be
  fetched again.

## Dashboards

- `Index.md` is generated by `wiki_tools.py index`.
  Never edit it by hand.
- `Log.md` gets entries through `wiki_tools.py log`,
  grouped under `## YYYY-MM-DD`, oldest first. One line
  per change, naming pages with `[[links]]`.
- `Topics.md` is the plan: main topics and keywords.
- Write other dashboards by hand when an overview helps:
  `Home.md` (front page), `Architecture.md`,
  `Decisions.md`, `Glossary.md`.

## How an agent reads the wiki

No server needed. Plain files, find and grep:

```bash
T=~/.claude/wiki/wiki_tools.py
python3 $T grep "webhook"               # or: grep -rin webhook wiki/
python3 $T find "*Billing*"             # or: find wiki -name "*Billing*"
python3 $T read "Wiki/Entities/Stripe.md"
python3 $T backlinks "Stripe"           # who links here
```

1. Start at `Dashboards/Index.md` or grep for the term.
2. Open the best page; follow `[[Name]]` by finding
   `Name.md`.
3. For exact wording, follow a Summary's `source_file`
   into `Raw/`.
4. Check claims about code against the code. When they
   disagree, the code wins; fix the page.

## Tools

| Command | Does |
|---|---|
| `wiki_tools.py init` | create the skeleton; never overwrites |
| `wiki_tools.py check` | lint; exit 1 on errors |
| `wiki_tools.py index` | rebuild `Dashboards/Index.md` |
| `wiki_tools.py log "text"` | add a dated log line |
| `wiki_tools.py find/grep/read/backlinks` | search |
| `server_start.sh` / `server_stop.sh` | web UI on port 8020 |

`check` errors: missing folder, page without `type`,
duplicate page name. Warnings: dangling link, orphan
page, page missing from Index, Raw file with no summary,
items waiting in `Inbox/`.

---

Created: 2026-09-15
Last updated: 2026-09-15
