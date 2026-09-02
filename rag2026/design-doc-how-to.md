# How to Create a Software Architecture Design Document

A practical guide to producing a design document that engineers will
actually read, approvers will actually sign, and implementers can
actually build from.

This guide was distilled from a real project: a knowledge-base system
for millions of documents that went from a formal spec to a polished
story-style document over roughly thirty rounds of dialogue. The
examples come from that project; **the method applies to any system.**

---

## Contents

1. [What This Document Is, and What It Isn't](#1-what-this-document-is-and-what-it-isnt)
2. [The Working Method](#2-the-working-method)
3. [The Guiding Principles](#3-the-guiding-principles)
4. [The Skeleton](#4-the-skeleton)
5. [The Sections Everyone Forgets](#5-the-sections-everyone-forgets)
6. [Writing It as a Story](#6-writing-it-as-a-story)
7. [The Prompt Playbook](#7-the-prompt-playbook)
8. [Producing the PDF](#8-producing-the-pdf)
9. [Definition of Done](#9-definition-of-done)
10. [Anti-Patterns](#10-anti-patterns)

---

## 1. What This Document Is, and What It Isn't

Two documents get confused constantly, and mixing them up wastes weeks.

| | **PRD** (Product Requirements Doc) | **ADD** (Architecture Design Doc) |
|---|---|---|
| Written by | Product / project manager | Engineers |
| Written for | Everyone | Engineers |
| Answers | *What* should it do, and *why* | *How* will we build it, and *why that way* |
| Contains | User needs, business goals, success criteria | Components, contracts, data models, trade-offs, numbers |

The flow is one-directional:

```
PRD  →  Architecture Design  →  Implementation
```

**This guide is about the middle box.** The PRD is an input. If you
don't have one, extract the requirements from whoever is asking and
put them in an appendix, because a design that can't point at the
requirement it satisfies is just an opinion with diagrams.

### What a good ADD does

- **Decides.** It names the choice and the reason, not a menu of options.
- **Quantifies.** Sizes, latencies, throughput, costs, growth. Numbers
  turn arguments into arithmetic.
- **Stays falsifiable.** Every bet has a written threshold at which
  you'd change your mind.
- **Survives contact with reality.** It covers the boring lifecycle
  work, not just the exciting steady state.
- **Can be read in one sitting.** If nobody finishes it, it didn't
  happen.

---

## 2. The Working Method

A design document is not written in one pass. It grows through cycles:

```
question  →  clarification  →  fold the clarification back in
```

**The reader's questions are your best signal for what the document
fails to explain.** Every time someone asks "wait, is X stored in files
or in the database?", you have found a real gap. Answer them in plain
language first, with analogies and concrete examples. Then fix the
document so the next reader never has to ask.

### Five phases

**Phase 1: Formal draft.** Get the substance down: requirements,
principles, architecture, data model, sizing, risks. Ugly is fine.
Complete matters more than pretty.

**Phase 2: Interrogate it.** Go through the [prompt
playbook](#7-the-prompt-playbook). Confirm what it claims, challenge
what it assumes, add the forgotten sections. Expect this phase to
double the document's length.

**Phase 3: Consolidate.** The document grew by accretion and now it
shows: repeated ideas, sections in the wrong order, three explanations
of the same thing. Re-read the whole thing and rewrite it shorter.
*This step is not optional.* Incremental growth always produces a
document that is 30% longer than it needs to be.

**Phase 4: Story rewrite.** Convert the formal spec into a narrative
of challenges and solutions. See [section 6](#6-writing-it-as-a-story).

**Phase 5: Produce and verify.** Table of contents, diagrams, PDF,
final read-through.

### Four rules for the whole ride

1. **Propose before editing.** When someone asks "does it make sense
   to add X?", they want an assessment, not a rewrite. Give the
   assessment, ranked by value against cost. Edit when told to.
2. **Preserve before destructive rewrites.** Before restructuring
   (formal → story, say), commit to git or save the old version under
   a distinct name. Say where the backup is.
3. **Verify claims against the actual text.** "Please confirm the
   design does X" means *go read it and cite the section*. If it
   doesn't do X, say so plainly.
4. **Markdown is the source of truth.** PDFs, HTML, and rendered
   diagrams are projections. Regenerate them; never hand-edit them.

---

## 3. The Guiding Principles

These are the durable core. They transfer to any system: a payments
platform, a data pipeline, an IoT fleet, a game backend. Keep them,
adapt the examples.

### 3.1 Simplicity is the guiding principle

Choose the simplest architecture that still delivers the **full**
functionality: the minimum number of moving parts, each one chosen
deliberately.

Simplicity is what makes a project:

- **Do-able**: it can actually be built and shipped
- **Flexible**: fewer parts to rearrange when requirements change
- **Maintainable**: fewer things that break, fewer experts required
- **Affordable**: no fleet of clusters, no heavy hardware, no big team
- **Fast to prototype**: something real in front of users in weeks

Complexity in architecture and infrastructure can bring a project to
its knees. Projects rarely die from missing features; they die
drowning in their own plumbing, often before the first user asks the
first question.

In practice this means: prefer one well-understood system over several
specialized ones. Prefer a SQL join over a new service. Prefer boring
technology the team already runs. *Complexity must justify itself with
evidence; simplicity is the default and needs no justification.*

> **Worked example.** The reference project resisted the standard
> five-system stack (vector DB + search cluster + message broker +
> workflow engine + graph DB) and put everything in one PostgreSQL
> cluster: registry, entitlements, vector index, keyword index, job
> queue, audit log. Justification was arithmetic: 20 to 25 million
> chunks is not big data. Access control became a SQL join instead of
> a distributed-systems research project.

**Simplicity is not minimalism.** Do not sacrifice required
functionality, correctness, security, or auditability for it. And do
not confuse "simple" with "quick hack". Simple designs are usually
the result of *more* thought, not less.

### 3.2 Make the bets falsifiable: write down scaling gates

Every simplification is a bet. Bets that can't lose are dogma. So for
each one, write the **measurable threshold** at which you would change
your mind:

> *We stay on one database until any of: chunk count above 50 million;
> p95 latency above 2 seconds despite tuning; index churn degrading
> reads. When a gate trips, we migrate as a background re-index, not
> a crisis.*

Now the review conversation changes shape. Instead of "will this
scale?" (unanswerable, infinite), it's "which gate are we near?"
(a number, checkable on a dashboard).

### 3.3 Modularity: don't let the dumplings fuse

Simplicity has an evil twin that shows up wearing simplicity's clothes:
**the small system that nobody can change.**

Think of a good system as a plate of dumplings. Each has a wrapper
that keeps its filling to itself (*encapsulation*), holds its own
distinct filling (*separation of concerns*, a *bounded context*), can
be cooked and tasted on its own (*developed and tested separately*),
and sits loosely beside its neighbors, touching but never sticking
(*loose coupling*).

The failure mode is boiling them too long. A lean team builds a clean
system. Then, under deadline, one component queries another's tables
directly (why bother with an API for an internal tool?). A parser
learns which model is downstream (it was convenient). Every shortcut
is individually reasonable. Two years later the dumplings have **fused
into one messy clump**. The diagram still shows few boxes, but you
can't change *any* of them without understanding *all* of them. The
system is small, and it is stuck.

This matters doubly when the design makes bets, because the scaling
gates promise a calm migration. That promise is only honest if the
thing behind the gate can be swapped without a rewrite.

**So: every capability owns its domain and is used only through its
contract.**

- **Services, not schemas.** Consumers call the API; not one of them
  knows a table name.
- **External systems are plugins.** Each source, vendor, or provider
  speaks its own dialect on one side and emits the same normalized
  events on the other. Adding one means writing an adapter, not
  performing surgery on the pipeline.
- **Implementations hide behind a contract.** Two parsers, two
  payment providers, two model families, all with the same output
  shape. A better one next year changes nothing downstream.
- **Dependencies point one way.** Domain ← application ← adapters ←
  bootstrap. Nothing downstream ever writes upstream. Water flows
  downhill only.
- **Wiring is explicit.** Concrete implementations are selected in one
  small composition root. No service locators, no import-time
  registration, no global mutable state, no monkey-patching.

The test for every boundary is blunt: **can this piece be changed,
replaced, or removed without understanding the whole system?** If not,
the seam is in the wrong place.

### 3.4 Modularity reaches into the code

A module with beautiful external contracts can still rot from within:
one 3,000-line file, functions that scroll like film credits, not a
word of explanation. That's the dumplings fusing one level down. Put
these limits in the design document, not just in a style guide:

- **Files under 800 lines.** A longer file holds more than one
  responsibility and should be split.
- **Functions under 50 lines.** A function that doesn't fit on one
  screen is several functions in a trench coat.
- **Docs at every level.** Each file opens with a doc block stating
  its purpose; every function and class carries its own. Code explains
  *how*; docs explain *what for*.
- **Directories are modules, and each has its own `README.md`**
  stating what it owns, its public API, what it depends on. A newcomer should
  be able to parachute into any directory and know where they landed.

### 3.5 One system of record

Name the single place where truth lives. Everything else is a copy, a
cache, or a projection, and is labeled as such. Consistency becomes a
transaction instead of a distributed-systems project.

The corollary is a rule with teeth: **projections are never edited by
hand.** They are rendered from the source of truth and can be deleted
and regenerated without losing a byte.

### 3.6 Do the expensive work once; everything downstream is disposable

Identify the step that costs weeks of compute or money (parsing,
training, transcoding, geocoding, enrichment) and store its output
permanently. Everything after it reads from *that*, never from the raw
input.

This single decision is what makes future migrations boring:

> *Re-chunking, re-embedding, upgrading models, even defecting to a
> different search engine: all of it reads from stored derivatives.
> The entire search layer is disposable.*

And boring migrations are the good kind.

### 3.7 Choose boring technology, and justify the language

Someone will ask "why not rewrite it in \<faster language\>?" in the
design review. Answer it *in the document*, once, with reasoning
anyone can check:

- **Where does the time actually go?** If the hot paths already run in
  C, CUDA, or the database engine, then rewriting the orchestration
  layer makes the glue faster, and the glue was never the bottleneck.
- **Where does the ecosystem live?** Abandoning the best libraries for
  the job to gain type safety in the plumbing is a bad trade.
- **Who maintains it?** The pool of people who can keep the system
  running is a real architectural constraint.
- **Keep it reversible.** If one module ever proves to be the
  bottleneck *under measurement*, modularity lets you reimplement that
  one module behind the same contract. No crisis, no rewrite. A swap.
  (Though the honest first answer to a slow worker is usually even more
  boring: add another worker.)

### 3.8 Trust is re-earned continuously

Systems break in two ways, and both are silent.

**Code changes**, and no compiler complains when someone imports the
database driver into the domain logic or bypasses the public API "just
this once."

**Data changes**, and quality degrades quietly: a connector dies on a
Tuesday and nobody notices until someone asks about the gap; an
upgrade shifts rankings and accuracy drops three points with no error
message anywhere. Silence is not a good sign. Silence is just silence.

So verification runs at both timescales.

**Guarding the code, a pyramid of tests:**

| Layer | Guards | Method |
|---|---|---|
| **Unit** | Functions | Fast, isolated, no network, no DB; dependencies faked at the port interfaces |
| **Module** | Contracts | Each module tested through its **public API**, dependencies stubbed |
| **Integration** | Real seams | Real database in a disposable container (pinned by digest); pipeline end-to-end against a fixture dataset |
| **Architecture conformance** | The rules themselves | Mechanical: `import-linter`, file/function-length and docstring checks in CI. Judgment: **an AI agent reviews every change against the written architecture rules**, flags the specific rule it believes is broken, and gates the merge |

That last row is worth the trouble. Mechanical tools catch mechanical
violations; an agent catches "is this new dependency direction
legitimate?" and "is this utility module quietly becoming a junk
drawer?" Humans adjudicate disputes; the agent just makes sure erosion
never happens *silently*.

Note also that unit tests are only *possible* because the ports exist.
Modularity pays its first dividend here. And untested code develops a
second disease: nobody dares touch it. A codebase that can't be safely
changed is the fused clump's final form: frozen solid.

**Guarding the behavior, with evals grown from real outputs:**

For any system with judgment in the loop (an AI feature, a ranking
model, a fraud score, a recommendation), code tests prove the machine
runs; a separate discipline proves it's still *right*.

The tempting shortcut is a conference-room checklist: "outputs should
be accurate, relevant, and clear, scored 1 to 10." Checklists born
this way fail twice: the scores are too mushy to act on, and the
criteria only cover failures somebody predicted. Real failures have
more imagination than that.

- **Start from real outputs and traces, not an abstract checklist.**
- **Review failures before writing criteria.** Put real traces
  (input, routing decision, everything retrieved with its scores, and
  the final output) in front of domain experts, who annotate problems
  *in context*.
- **Split criteria two ways.** *Top-down*: what the task always
  required (format, length, policy compliance, citation present).
  *Bottom-up*: recurring flaws found by comparing real outputs against
  human-approved ones. These are patterns no whiteboard session would
  produce.
- **Prefer specific pass/fail checks over vague scores.** Not
  "faithfulness: 7/10" but "every numeric claim appears in a cited
  source: yes or no." Binary checks are debuggable; a failure points
  at exactly one thing to fix.
- **One judge pass per criterion.** A single mega-prompt asked to
  verify twelve requirements will quietly forget a few; twelve small
  judges with one question each forget nothing.
- **Let AI do the labor, humans supply the taste.** AI clusters
  similar failures, surfaces patterns, builds the review interface,
  drafts rubric items. Only the domain expert knows which paraphrase
  is *materially* wrong.
- **Graduate every validated pattern into permanent machinery**: a
  regression case, a CI check, a dashboard series, a production
  monitor. The suite becomes the accumulated memory of every way the
  system has been caught being wrong. It only grows.

**And gate on it.** A nightly run against production compares against
a rolling baseline; a regression beyond threshold pages on-call and
*freezes updates* until a human understands why. A failed eval is
treated exactly like a failed deploy, because that's what it is.

Add two cheap checks that catch what test suites can't:

- **Reconciliation counts** across layers (source → registry →
  serving), so a silently dead connector shows up as a mismatched
  number *tonight*, not as a mystery at quarter-end.
- **Self-retrieval probes**: sample what changed today, generate a
  query from its own content, verify it comes back. Proof that new
  content is *findable*, not merely stored somewhere warm.

One principle at both timescales: **a failing test blocks the merge; a
failing eval freezes the pipeline. The system proves it still works
after every change, or the change doesn't ship.**

### 3.9 Self-healing

Detection is only half a nervous system. At scale, something is
*always* slightly broken: a worker dies mid-job, a file quietly rots, a
connector drops an event, an index puts on dead weight. If every small
failure needs a human, the on-call engineer becomes the immune
system, and humans make terrible white blood cells. They sleep, they take
vacations, they burn out. Meanwhile small failures wait in line, and
small failures that wait long enough grow up to become incidents.

**So: when something goes wrong, the system cleans and repairs itself.
Humans get paged for the exceptional, never for the routine.**

| Failure | Reflex |
|---|---|
| Crashed worker | Idempotent jobs in a transactional queue; the lock expires, the next worker picks it up. Re-running a finished step is a no-op |
| Corrupted file | Weekly scrub detects hash mismatch → quarantine → restore from the most recent *verifying* snapshot → re-check → file a report the human reads over coffee, after the repair |
| Missed event | Reconciliation doesn't just detect gaps, it queues the refetch. Detection and repair are one motion |
| Degraded index | Recall check finds the sagging partition → re-index in the next maintenance window, scheduled automatically |
| Anything derived | Throw it away and rebuild it. The universal repair tool is gloriously dumb |

Note how [3.6](#36-do-the-expensive-work-once-everything-downstream-is-disposable)
pays compound interest here: when everything downstream is disposable,
self-healing rarely requires cleverness, just a rebuild job and
patience.

**Self-healing has manners.** Retries use backoff and give up after a
set number of attempts; a job that keeps failing retires to a
dead-letter state and pages a human, because infinite retry is not
persistence, it's a tantrum. And name the categories that are **never**
repaired by automation guessing: typically permissions, money, and
regulated records. Anything ambiguous there escalates to people
immediately. *The system heals itself; it does not improvise itself.*

The quiet payoff: the team's time goes into making the system better
instead of holding it together. A platform that needs constant human
attention isn't simple, no matter how few boxes are on its diagram.

### 3.10 Don't chase the latest version

The design keeps data inside the perimeter, and then a developer
types `pip install` and the build downloads whatever was uploaded
yesterday, by anyone. Modern supply-chain attacks live exactly there:
hijacked maintainer accounts shipping poisoned point-releases,
typosquats waiting for one mistyped name, backdoors in build scripts.
The freshest package is the least reviewed package. **"Latest" is not
a version. It's a gamble.**

**Every dependency goes through quarantine: pinned, aged, verified.**
Like new hires, packages need a probation period.

- **Runtime** from a pinned major.minor line, upgraded on purpose
  (`brew install python@3.12`), never by accident.
- **Packages** managed with `uv` under two standing rules: nothing
  published in the last 30 days, no prereleases:

  ```toml
  [tool.uv]
  exclude-newer = "30 days"    # ignore anything published this month
  prerelease = "disallow"      # never alphas, betas, or RCs
  ```

  Upgrades become an explicit, reviewable act:

  ```bash
  uv lock --upgrade
  uv sync
  ```

  Or, for a `requirements.txt` flow:

  ```bash
  uv pip install --upgrade   --exclude-newer "30 days" -r requirements.txt
  uv pip install --reinstall --exclude-newer "30 days" -r requirements.txt
  ```

  The lockfile is committed, so laptop, CI, and production resolve to
  byte-identical, properly-aged packages. No surprises, which is the
  highest compliment in operations.
- **Databases and services** on a pinned major line from the official
  repository. Minor releases adopted weeks after they ship. A brand-new
  major, the dreaded `.0`, never goes straight to production;
  rehearse it on the restore-test instance that conveniently already
  exists.
- **Container images** get the strictest treatment, because a tag is a
  promise nobody has to keep: official images only, pinned **by
  digest** (`postgres:16.6@sha256:...`), `:latest` banned outright,
  pulled once into an internal registry and scanned on the way in.

### 3.11 Don't forget the humans

A design can be very generous to machines (APIs, queues, contracts,
agents everywhere) and offer humans nothing. A system without windows
gets operated by SSH, which is a fancy way of saying "an incident
waiting for a typo."

Every system needs at least:

- **A command center**: dashboards showing health, lag, quality
  trends, reconciliation deltas, and *what the self-healing did
  overnight* (the morning-coffee report); plus controls to start,
  pause, re-run, and re-index.
- **An operator's chat**, if agents are in play: the command center's
  conversational twin, which can *explain* as well as display.
- **The end-user surface**: whatever the system exists to provide,
  with an easy way for users to flag bad results straight into the
  evaluation queue. The complaint department feeds the immune system.

Two rules keep interfaces honest: **every button drives the same
documented, audited APIs** used everywhere else (no private tunnel to
the database; a dashboard is a view with steering, not a backdoor);
and **state-changing actions require confirmation and land in the
audit log** with an identity attached.

House style for the frontend: **vanilla JavaScript, no frameworks, no
build step.** For a handful of dashboards and panels, a framework is
another dependency to quarantine, another supply chain to audit, and
another migration in five years when it falls out of fashion. Keep it
modular (small ES modules, one per feature), obey the same size and
doc limits as the backend, and put **all styles in one `styles.css`**.

### 3.12 Give the work an owner

The system isn't maintained by "the system." It's maintained by people
who re-run bad batches, review low-confidence output, resolve
conflicts, and chase the connector that's been sulking since Thursday.
That work needs owners, statuses, and handoffs. Otherwise it lives in
email threads and in the heads of people who might be on a beach next
week.

So give maintainers a task system. (The reference project calls a task
a **monkey**: the next move, the thing on your back that needs to hop
off. Name yours whatever makes the team smile.)

The elegant part is where the tasks come from: **the system already
produces them.** Every escalation path in the design gets an inbox:

- A job exhausts its retries → the dead-letter entry *becomes a task*.
- The nightly gate trips → a task, with the regression report attached.
- A user flags a bad result → a task, with the trace included.
- The scrub can't restore a file; reconciliation can't refetch a record
  → tasks.
- And humans create their own: cleanup campaigns, onboarding drives.

The immune system files tickets. Then the mechanics are deliberately
ordinary: each person sees *their* tasks; tasks pass between people
(vacation transfers the whole troop in one action, nothing orphaned);
a group dashboard shows who's drowning and who's idle, because a task
system where managers can't see the pileup is just a diary.

Architecturally, keep this a **separate app** with its own API and its
own frontend. The core service stays lean and stable while the
maintainers' workbench evolves at business speed.

And let maintainers build their own tools by **vibe-coding**: describe
the review screen or one-page dashboard, let an AI assistant generate
it over the existing APIs, ship it in an afternoon, no platform-team
ticket. Vibe-coding gets guardrails rather than a leash: generated
tools live inside the maintainers' app, reach data only through documented APIs
(so access control and audit apply automatically; a generated page
cannot see what its author can't), and pass the same CI, size limits,
and conformance review as human-written code. Fast where speed is
cheap, gated where mistakes are expensive.

---

## 4. The Skeleton

Adapt freely. Cut what doesn't apply, add what your domain demands.
The order matters: it's the order a reader needs to learn things.

**Front matter**

1. **Title + status line**: `Status: Draft (pending approval) · Date: ...`
   No version numbers in file names; no changelog at the top. *Git is
   the changelog.*
2. **Executive summary**: 3 to 5 short paragraphs covering the scale
   headline, the key architectural bets, the resource footprint. Write it last,
   place it first.
3. **Table of contents** with working anchor links.

**The body**

4. **The problem**: what's broken today, told concretely. Then the
   fine print: the constraints that make it hard (compliance, scale,
   latency, cost, data residency).
5. **Explicit non-goals**: what v1 deliberately does *not* do. As
   load-bearing as the requirements, and the cheapest scope protection
   you will ever write.
6. **The simplicity bet**: the architecture, why it has this few
   parts, and the scaling gates that would change your mind. Include
   the language/platform justification here.
7. **Modularity**: the seams, the contracts, the dependency
   direction, and the code-level rules.
8. **Storage and data model**: where things physically live, with
   actual DDL or schemas. Include the durability disciplines
   (content addressing, write-once, immutability) if they apply.
9. **The processing pipeline**: how input becomes usable output, with
   the "expensive work once" boundary marked.
10. **The core domain sections**: three to six sections specific to
    your system. This is where the interesting design lives.
11. **Lifecycle**: add / update / remove propagation. *See
    [section 5](#5-the-sections-everyone-forgets).*
12. **Verification**: the test pyramid and the evaluation gate.
13. **Self-healing**: the repair reflexes and their limits.
14. **Correctness contract**: what the system guarantees about its
    output, and what it does when it doesn't know.
15. **Human interfaces**: the doors people walk through.
16. **Task ownership**: who fixes what, and how it gets handed off.
17. **Disaster recovery**: the day everything goes wrong.
18. **Sizing**: disk, memory, database, growth, backup overhead, with
    the arithmetic shown.
19. **Dependency discipline**: the supply-chain rules.
20. **Roadmap**: phases with timeframes; trust-building work
    (evaluation, sign-offs, DR drills) scheduled *before* scale-out.
21. **The shape of the thing**: the whole design distilled to N
    decisions (six to eight), simplicity first. This is the section
    executives will read. Make it the best writing in the document.

**Appendices**, the formal reference material, kept out of the
narrative so it doesn't slow anyone down:

- **A. Requirements** with stable IDs: Functional (F1...), Security and
  Compliance (S1...), Non-Functional (N1... with *measurable* targets:
  latency percentiles, RPO/RTO, SLAs). IDs make review possible.
- **B. Technology choices**: layer / selection / why. One row per
  decision, the "why" written for someone who will challenge it.
- **C. Risk register**: risk / engineered mitigation. Condensed.

**Diagrams** (SVG, so they render on GitHub and in Obsidian): overall
architecture, data layout, the main workflow, the roadmap. Four good
diagrams beat forty mediocre ones.

---

## 5. The Sections Everyone Forgets

Formal drafts describe systems **at rest**. Reality is motion. These
are the sections reviewers ask for after the first draft. Write them
before they have to.

**Lifecycle: what happens when data changes.** Every derived artifact
must be updated when something is added, updated, or removed. Miss one
layer and the layers start lying to each other. Include a **propagation
matrix** (event × artifact → mechanism and latency) and the hard rules:

- **Soft-deactivation, never deletion**, when history must remain
  citable.
- **Atomic visibility flips**: old off, new on, in one transaction.
  No query ever catches a record half-dressed.
- **Permission changes outrank everything.** Stale content is
  embarrassing; stale permissions are a breach. Give them their own
  SLA (minutes), their own alert, and a daily full re-sync to sweep up
  anything a missed webhook dropped.

**Continuous evaluation.** Covered in [3.8](#38-trust-is-re-earned-continuously).
The thing to remember at outline time: it needs its own section, not a
paragraph.

**Self-healing.** Covered in [3.9](#39-self-healing).

**Backup and recovery.** Start with the unpopular truth: **replicas
are not backups.** A standby will faithfully replay your `DROP TABLE`
within milliseconds. That's its job, and it's very good at it.
Replication protects against hardware failure; backups protect against
mistakes and malice, which have no SLA. Then specify:

- **Data tiers**: what is irreplaceable vs. reconstructible.
- **RPO and RTO as numbers** ("lose at most one hour; be back within
  eight").
- **Backups out of blast radius**: separate account, independent
  credentials, snapshot locks, write-once archives. No single
  compromised admin should be able to torch both the data and its
  safety net in one evening.
- **Restore *ordering***, because components must agree with each
  other afterward. Write the sequence down; it is not obvious under
  pressure.
- **Scheduled restore tests**, because a backup that's never been
  restored is a rumor. Monthly automated restore + verification;
  quarterly timed drill; a failed restore pages like a production
  outage.

**Sizing with the arithmetic shown.** `3M docs × ~1 MB ≈ 3 TB`. Give
tables for storage and for the database, a steady-state total, and a
provisioning recommendation with headroom. Readers always ask; pre-empt
them. And sizing is what makes a simplicity bet look *rational* rather
than reckless.

**Human interfaces and task ownership.** [3.11](#311-dont-forget-the-humans)
and [3.12](#312-give-the-work-an-owner).

---

## 6. Writing It as a Story

A formal spec is precise and nearly unreadable. People skim it, miss
the reasoning, and re-litigate settled decisions six months later.

**The fix: same technical substance, told as a sequence of challenges
converted into solutions.** Nothing is dumbed down. Every number,
every threshold, every trade-off stays. Only the *order of
presentation* changes, from taxonomy to narrative.

### The shape of a section

Each section is **one concrete challenge**:

1. **Open with the problem, vividly.** A scene, a failing query, an
   uncomfortable truth. *"Somewhere in there is the answer to almost
   any question a lawyer might ask. Nobody can find it."*
2. **Explain why the obvious answers fail.** This is where the reader
   earns the right to the solution, and where you pre-empt the
   reviewer who was about to suggest exactly that obvious answer.
3. **Deliver the solution in a bolded sentence.** *"**So the solution
   is a bet on gloriously boring technology:** one PostgreSQL cluster
   holds everything transactional..."* One scannable line per section
   means a skimmer still gets the architecture.
4. **Keep the rigor.** Numbers, thresholds, schema shapes, SLAs: all
   of it stays. Story style is a delivery mechanism, not a diet.
5. **Close by connecting forward or back.** *"File that fact away; it
   becomes the hero of 'The Day Everything Goes Wrong.'"*

### Rules of the style

- **No "Prologue", "Chapter N", or "Epilogue".** Plain evocative
  headings: *"The Day Everything Goes Wrong"*, *"What Was True Last
  March?"*, *"Where Do Three Million Files Live?"* A good heading is
  the section's question.
- **Cross-reference by name or idea, never by number.** Numbers break
  when sections move; names don't.
- **Concrete numbers over adjectives.** Not "highly scalable" but
  "20 to 25 million chunks, which for a well-fed PostgreSQL instance
  is a Tuesday."
- **Short declarative sentences for the punches.** *"Nobody can find
  it."* *"Silence is just silence."* *"Latest is not a version."*
- **Explain *why* before *what*.** The reason makes the decision
  memorable; the decision alone is just trivia.
- **Tables only for genuinely tabular data.** Prose for reasoning.
- **Light, not cute.** A little wit keeps a forty-page document alive:
  *"a function that doesn't fit on one screen is several functions
  in a trench coat"*. But the joke must carry the point, not replace
  it. If a sentence is only funny, cut it.
- **Use words your readers know.** The reference document originally
  called a section "Avoiding the Pelmeni Architecture." Most readers
  don't know *pelmeni*. It became "Don't Let the Dumplings Fuse",
  and the metaphor got sharper in the process, because the problem
  isn't dumplings, it's dumplings *fused into a clump*. **When a
  metaphor needs a footnote, replace it.**
- **Distill at the end.** Close with "the whole design is N
  decisions": six to eight numbered items, simplicity first.
- **Keep the formal material as appendices.** Requirement tables, tech
  choices, risk register. Implementers and approvers need them; the
  narrative doesn't.

### Keep both versions?

Optional. If approvers want a formal spec, keep `<name>-formal.md`
alongside the story version. Usually the story version plus appendices
is enough. One document that everyone reads beats two that nobody
finishes.

---

## 7. The Prompt Playbook

These are the moves that actually produced a good document, in roughly
the order they were used. Steal them verbatim; they're written to be
reusable.

### Establishing and checking

> *Current directory contains a design document for \<system\>. Please
> confirm that it \<does X\>. **Please don't change anything. Only
> propose improvements.***

The "don't change anything" clause is the most valuable half-sentence
in this playbook. It separates assessment from action and prevents a
question from becoming an unwanted rewrite.

> *So we will have: \<A\>, \<B\>, \<C\>, \<D\>. Correct?*

Forces an explicit mapping between your mental model and the document's
vocabulary. Ask for a table: your term → the design's term → status.

> *I am confused about \<X\>. Is it stored in files or in the
> database?*

Confusion is diagnostic. Whatever confused you will confuse the next
reader, so after the plain-language answer, fix the document.

### Finding the gaps

> *\<Method A\> and \<method B\> can't handle \<problem class\>. Does
> it make sense to also add \<C\>?*

> *Please suggest changes to describe: the process of updating the
> system when \<data is added / removed / updated\>, including every
> derived artifact.*

> *Please suggest changes to describe the process of evaluating the
> accuracy and completeness of the system after daily updates.*

> *Does the design include an interface for humans to work with this
> system?*

> *Please make sure the document prescribes creating tests: unit
> tests, per-module tests, integration tests, and tests using AI
> agents to confirm that code changes don't violate the architecture
> rules.*

> *Can we make improvements using techniques from \<URL\>?*

For this last one, ask for three buckets in the answer: **already
covered** (say where), **worth adopting** (concrete changes), and
**marginal** (mention, don't build). Also ask what *doesn't* transfer,
because domain differences matter.

### Injecting principles

> *Can you please express **simplicity** as a guiding principle? We
> choose architectures that are simple and elegant, minimizing moving
> parts while retaining functionality. Simplicity makes the project
> do-able, flexible, maintainable, affordable, fast to prototype: no
> big team, no heavy hardware. Complexity in architecture and
> infrastructure can bring a project to its knees.*

> *Please add **modularity** as a key principle. Explain it in the
> usual story-telling manner: problem → solution.*

> *Please add one more principle, **self-healing**. When something
> goes wrong, the system should be able to self-clean and self-repair.*

> *In the modularity section, add that code should be split into small
> pieces and well documented: files under 800 lines, functions under
> 50 lines, a doc at the top of each file, a doc for each function and
> class, subdirectories for modularity with a `README.md` in each.*

> *Does it make sense to rewrite the system in \<other language\>?
> Please add text explaining why \<chosen language\> is selected.*

Note the pattern: **name the principle, state the reasoning in your own
words, and ask for it in problem→solution form.** Principles inserted
this way land as arguments the reader can follow, not as slogans.

### Restructuring

> *Please rewrite the design document in engaging story style.
> Currently the style is formal and informative; it is difficult for a
> human to consume. Rewrite it as a story, explaining the challenges
> and converting them into solutions.*

> *Please don't use the words "Prologue", "Chapter", "Epilogue".*

> *Please add a table of contents at the beginning.*

> *We were adding topics incrementally and the document kept growing.
> Please review the whole document again to see if it can be
> rearranged or rewritten to be shorter and more elegant.*

> *Is it possible to rewrite the text to make it lighter? More playful
> and engaging?*

> *I don't like the title "\<X\>". Most people don't know that word.*

> *Please make a short bulleted list of the main architecture
> principles from our document.*

That consolidation prompt deserves special mention. **Run it whenever
the document has grown by more than about 20% since the last one.**
Documents grown by accretion always carry duplication their author
can't see.

### Finishing

> *Please remove the version number from the file names. Please remove
> the changelog at the top.*

> *Please add a short executive summary at the top, emphasizing
> \<the headline facts\>.*

> *Please add an estimate of the required disk space and database
> size.*

> *Please generate a nice PDF formatted for US Letter paper with 0.7"
> margins.*

> *Please update the document and the PDF accordingly.*

Say "and the PDF" every time. Otherwise the PDF silently drifts out of
sync with the Markdown, and you will hand someone a stale artifact at
exactly the wrong moment.

---

## 8. Producing the PDF

A proven pipeline with no LaTeX dependency:

1. **Markdown → HTML**
   ```bash
   pandoc -f gfm -t html5 --standalone --css=.pdf-style.css \
          design.md -o build/design.html
   ```
2. **HTML → PDF** with WeasyPrint.
3. **CSS** (keep it in the repo as `.pdf-style.css`):
   - `@page { size: Letter; margin: 0.7in; }` plus page counters in
     margin boxes
   - `header#title-block-header { display: none; }`, because pandoc
     duplicates the title
   - `tr { page-break-inside: avoid; }` and `page-break-after: avoid`
     on headings
   - wrapped `pre` blocks, compact styled tables
4. **Rasterize SVG diagrams.** WeasyPrint mangles SVGs with embedded
   font styles. Use headless Chrome per diagram:
   ```bash
   chrome --headless --screenshot=out.png --window-size=1400,900 \
          --force-device-scale-factor=4 diagram.svg
   ```
   Swap `.svg` → `.png` references with `sed` **at build time only**.
   The Markdown keeps SVGs so GitHub and Obsidian render them.
5. **Verify the output.** Check page count and file size. Visually
   inspect the title page, a table-heavy page, and every figure page.
   Confirm TOC anchors resolve (`href="#..."` vs `id="..."` in the
   built HTML). Grep the extracted PDF text for newly added sections.
6. **Document the rebuild one-liner** in the repo, and regenerate
   after *every* content change.

Watch for mechanical damage along the way: corrupted escape sequences
(`\r`, `\t` eaten from things like `$\rightarrow$`), image paths
pointing at directories that don't exist, anchors broken by renamed
headings.

---

## 9. Definition of Done

- [ ] Scale, cost, and "how big is this really?" are answered **with
      numbers**, arithmetic shown.
- [ ] **Simplicity** is stated as a principle, and every component
      earns its place against it.
- [ ] Every architectural bet has a **written scaling gate**.
- [ ] **Modularity** is specified at both levels: contracts between
      modules, size and doc limits inside them.
- [ ] **Lifecycle** (add / update / remove propagation) is described,
      not just steady-state architecture.
- [ ] **Verification** covers both timescales: a test pyramid gating
      merges, an evaluation gate gating updates.
- [ ] **Self-healing** reflexes are listed, along with what is never
      auto-repaired.
- [ ] **Backup and recovery** states RPO/RTO, restore ordering, and a
      restore-testing schedule.
- [ ] **Humans** have interfaces, and maintenance work has owners.
- [ ] **Dependencies** are pinned, aged, and verified.
- [ ] **Non-goals** are explicit.
- [ ] The document closes with **N decisions** anyone can quote.
- [ ] A newcomer can read it in one sitting; an implementer can build
      from it plus the appendices.
- [ ] The PDF is regenerated, verified, and matches the Markdown.

---

## 10. Anti-Patterns

| Anti-pattern | What it looks like | Fix |
|---|---|---|
| **The vendor stack** | Five specialized systems because every reference architecture has five | Do the arithmetic. Write the scaling gate. Start with one |
| **The option menu** | "We could use A, B, or C, each with trade-offs..." | Decide. State the reason. Move on |
| **Adjective architecture** | "Highly scalable, robust, cloud-native" | Replace every adjective with a number |
| **Steady-state-only** | Beautiful architecture, no word on what happens when data changes | Write the lifecycle section |
| **The frozen checklist** | Quality criteria invented in a conference room, scored 1 to 10 | Grow criteria from real traces; binary pass/fail |
| **Version numbers in filenames** | `design-v4-FINAL-v2.md` | Git is the changelog. One filename, forever |
| **The changelog header** | Three screens of revision history before the content | Delete it. Git remembers |
| **Accretion bloat** | Each round adds a section; nothing is ever removed | Run the consolidation prompt every ~20% growth |
| **The unread masterpiece** | Technically perfect, forty pages, formal voice, nobody finishes it | Story rewrite |
| **Machines only** | APIs and queues everywhere, no dashboard, no chat, no task list | Three doors for humans; give the work an owner |
| **The footnoted metaphor** | A clever analogy the reader has to look up | If it needs a footnote, replace it |
| **Stale PDF** | The Markdown moved on; the PDF didn't | Regenerate every time. Say "and the PDF" in every request |

---

## A Closing Note

The best design documents are **interrogated into existence.** Nobody
writes one straight through. The first draft is a hypothesis. Every question a
reader asks is a bug report against your explanation. Every "wait, how
does that work?" is a section you owe them.

Answer honestly, fold the answer back in, and periodically stop adding
to rewrite what's there more simply. Do that thirty times and you end
up with something rare: a technical document people actually enjoy
reading, that an engineer can build from, and that still tells the
truth two years later about *why* the system looks the way it does.

That last part is the real deliverable. Code records what you built.
Only the design document records **why**.
