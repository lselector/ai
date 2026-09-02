--------------------------------------------

Current directory contains a design document for a RAG system for millions of documents.

Please confirm that it uses PostgreSQL for symantic search (Vector Similarity) and also full text search (keywords).

These methods can't help to understand the dependencies
between different pieces of information. The structure.

Does it make sense to also create an interconnected wiki
to help with understanding the structure and clustering ?

Please don't change anything - only propose improvements.

--------------------------------------------

To implement wiki, we would need to convert the documents into wiki files,
which are markdown files in Google Open Knowledge Format with links between files,
and we need to store those files in some directory structure for easy grep/find operations

--------------------------------------------

So we will have:

 - raw documents
 - processed files (after OCR, ...)
 - wiki versions of these documents (md files)
 - chunks and vectors in the database for keyword and vector search

 Correct?

--------------------------------------------

OK, please update the design document according to our conversation in this session

--------------------------------------------

- please remove the version number from the file names.

- please remove the Change log at the top of the document

- please add a short executive summary at the top emphasizing that
  the system is designed to work with millions of documents
  and include combination of search methods - symantic (vectors),
  keywords (full text search), and structure (wiki)

- please add an estimate of the required disk spaces and database size

--------------------------------------------

I am confused about wiki. Is it stored in files or in database?

--------------------------------------------

Can we make some improvements using techniques
from this project?

https://github.com/mempalace/mempalace

--------------------------------------------

Please generate a nice PDF formatted for US Letter paper with 0.7" margins

--------------------------------------------

Please suggest changes to the design document to describe 

- the process of updating the system when we adding/removing/updating docs (including versions, vectors, indexes, wiki, ...)

- The process of evaluation of the accuracy and completness of the RAG system and hallucination level after daily updates

--------------------------------------------

Please rewrite the design document in engaging story style.

Currently the style is formal informative.
It is difficult for a human to consume.

Please rewrite it as a story. Explaining the challenges - and converting them into solutions.

--------------------------------------------

I like the new document rewritten as a story.
But please remote this line at the top:
   **The Design, Told as a Story: Every Challenge and How We Solved It**

Also please don't use the words "Prologue", "Chapter", "Epilogue".

--------------------------------------------

Very good.
Please add the table of contents at the beginning


--------------------------------------------

It is much better now.
Can you please express simplicity as a guiding principle.

We are choosing architecture which is simple and elegant.
We are trying to minimize number of 
moving parts while still retaining 
functionality.

Simplicity makes the project "do-able",
flexible, maintainable, affordable. 
We can prototype fast.
We don't need a big team.
We don't need many systems or heavy hardware.

Whereas complexity in architecture and infrastructure can bring the project to its knees. 

--------------------------------------------

Please create a generic skill (a markdown file) for creating a design document for a software project similar to how we have done it here (see in myprompts.md).

--------------------------------------------

In current repository "ai"
I have .claude directory
which has two subdirectories - "rules" and "skills". 

.claude/rules
.claude/skills

Will Claude Code always use those rules?

Please  create root `CLAUDE.md` with the five imports

--------------------------------------------

Please create yet another rule instructing the agent to use "simplicity" when designing architectures or planning the code structure; to find simple, elegant, minimal solutions. To always try to simplify.

Please add this rule import to CLAUDE.md as well

--------------------------------------------

I want the rules I use in this repo to be applied 
to all projects on this computer.
Please add them under $HOME/.claude/ 
and make sure they are always loaded

--------------------------------------------

what is the difference between PRD document and architecture design document ?

PRD = Project Requirements Doc
written usually by project manager (human)

ADD = Architecture Design Doc - written by engineers for engineer. It takes PRD as input

PRD → architecture design → implementation

--------------------------------------------

Please add modularity as one of key principles into the 
rag-knowledge-base-design.md document
Explain it in usual story-telling manner: problem-solution.
Also update the pdf accordingly.

--------------------------------------------

Please update rag-knowledge-base-design.md
by go deeper into validating the system's accuracy.

Here are some concepts:

- AI evals (short for evaluations) are systematic tests 
used to measure the quality, accuracy, safety, 
and performance of AI models and applications.

- Start evals from real outputs and traces, 
not an abstract checklist. 

- Review failures before writing criteria
- Split criteria into Top-down and Bottom-up:
- Top-down: known task requirements, such as format, length, actionability, or policy compliance
- Bottom-up: recurring flaws discovered by comparing generated outputs with human-approved results

AI can help cluster examples, build a review interface, 
identify repeated patterns, and draft rubric items,
but humans supply the taste and product judgment

Prefer specific pass/fail checks over vague scores. 

Examples: “uses sentence fragments,” “answers a sales objection,” or “contains required structure.”

Use separate LLM-judge passes or subagents for many criteria; one large prompt can overlook requirements.

Annotate outputs in context. For writing, flag issues directly in the draft; for agents, review end-to-end traces.

Turn validated patterns into regression tests, dashboards, CI checks, and production monitoring.

--------------------------------------------

As we are using Python, please add some details:

use brew to install python on Mac or Linux
use uv for setting environment and install modules

Do NOT upgrade to latest versions.
Because latest versions may have problems (and even explits or viruses)

For example, in pyproject.toml add:

```
exclude-newer = "30 days"
prerelease = "disallow"
```

Then:

```
uv lock --upgrade
uv sync
```

Or:

```
uv pip install --upgrade --exclude-newer "30 days" -r requirements.txt

uv pip install --reinstall --exclude-newer "30 days" -r requirements.txt
```

Add similar instructions for installing PostgreSQL and docker images

--------------------------------------------

In the section about modularity please add that code should be split into small pieces
and well documented.

- Make files no longer than 800 lines.

- Make individual functions no longer than 50 lines

- Each file should have doc at the top

- Each function or class should have doc too

Code may be split into subdirectories for modularity. Each directory should have its own README.md file

--------------------------------------------

Please make sure that the document prescribes creating tests. There should be different types of tests - unit tests, test for individual modules, total tests, also tests using AI agents to confirm that the code changes do not violate the architecture rules.


--------------------------------------------

We were adding topics incrementally - and the docuemnt was gorwing. Please review the whole document again to see if it may be re-arranged (re-written) to make it shorter and more elegant

--------------------------------------------

Is it possible to rewrite the text to make it lighter? More playful and engaging?


--------------------------------------------

Please add one more principle - self-healing.
When something goes wrong - the system shoudl be able
to self-clean and self-repair

--------------------------------------------

Does it make sense to rewrite the system into Rust?

Please add some text to the design document explaining why Python is selected (and not Rust)


--------------------------------------------

Does the design include some sort of interface for humans to work with this RAG system?

As  minimum we need a command center and dashboards to control data loads and removal, updates, validation, testing
We need an agentic chat for administration.
And we need agentic chat for using the system

When designing the frontend, please use vanialla javascript (no react or other frameworks needed). Please do it modular, put all styles in one file.

Please make corresponding changes in the design document and PDF


--------------------------------------------

In real life the data in the system may be maintained and validated by several users. They may need to see their own tasks lists, the status, the failures. 

Let's call the tasks as "monkeys". Monkey is the next move. The task. The ticket. 

Each maintainer user may have different monkeys. 
When a user goes on vacation - his monkeys can be passed to someone else in the group. There should be a dashboard showing all the monkeys, theis status, etc.

This administrative/management should be implemented as a separate Fast-API web app.

Maintainers should be able to do vibe-coding to create their service interfaces as business requires. And to create and schedule workflows related to data extraction, cleaning, transformation, loading, verification, etc.

Please add this to the document



--------------------------------------------

I don't like the title "Avoiding the Pelmeni Architecture"

Most people don't know the word "Pelmeni".

I think it is better to use the word "dumplings".

And Pelmeni are not bad by themselves.
The bad thing is when they fuse into one messy clamp.
We want loose coupling, separation of concerns, encapsulation, bounded contexts. We want to be able to develop and test separate "dumplings" separately.

Please change the text accordingly

--------------------------------------------

Please make a short bulleted list of the main principles for designing the architecture from our document

--------------------------------------------

The vector similarity search relies on similarity of question (query) and text chunk. To make this work better, there is a common practice to pre-process the data (documents or text chunks) and the question to put them into similar format, so that you can "compare apples to apples". Please add this pre-processing as part of the system in the design

--------------------------------------------

Please add an option to do "fusion" to reduce hallucination level.  Fusion is when you use 2or 3 independent AI models to answer the same question - and then use a judge model to synthetize the answer and avoid hallucinations.

Another option is to use different "persona" when using the model to consider the answers from different perspectives

Please update the design doc

--------------------------------------------

Please create a markdown document

how_to_create_a_design_doc.md

with instructions how to create a software architecture design document.

Please use two files to guide you:

myprompts.md - prompts I have used
rag-knowledge-base-design.md - the final doc

The final doc is for creating RAG system.
I want you to create instructions which may be used to createe any other system. The guiding principles 
(like simplicity, modularity, etc.) should stay the same.
The instructions on using story style (sequence of problem-solution parts) stays the same. etc.


--------------------------------------------

Please update the  .claude/skills/design-doc/SKILL.md 
both in this repo and under $HOME/.claude

--------------------------------------------


--------------------------------------------
