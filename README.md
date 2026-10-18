---
title: Jira Issue Architect
description: A local-first bug reporting assistant that refines raw bug observations into structured drafts and checks them against an existing defect backlog before they become new tickets.
---

## Overview

Jira Issue Architect takes a raw "brain dump" of an observed bug and turns it into a clean,
structured draft report. Before that draft reaches the backlog, the tool checks it against
the existing defect database for duplicates and related work, and suggests components and
labels from an approved list. A human always reviews the final draft before anything is
submitted.

## Why this matters

Products that have been in active development for years accumulate backlogs with
thousands, sometimes tens of thousands, of reported issues. At that scale, nobody can
reliably know whether a bug has already been reported, discussed, triaged, or fixed. A
reporter files a new ticket in good faith, a developer picks it up weeks later, and only
during investigation does it surface that the same root cause was already analyzed and
resolved in a ticket from months earlier under completely different wording. The
investigation effort on the duplicate is wasted, and it is wasted a second time for every
additional duplicate that follows before someone notices the pattern.

Keyword search does not solve this at scale. Two reports describing the same crash rarely
use the same words: one reporter writes "app freezes on save", another writes "UI hangs
after clicking export", and a text match on either phrase misses the other entirely. The
larger the backlog grows, the less a human triager can hold in their head, and the more
these near-duplicate reports blend into noise. Catching the duplicate at submission time,
using semantic similarity rather than exact wording, prevents the wasted triage cycle
before it starts rather than discovering it after the fact.

### Additional points

> [!NOTE]
> The points in this section were added by the assistant based on the problem statement,
> not supplied by the project owner. Review them and treat anything here as a candidate for
> future scope rather than a committed requirement.

* A duplicate surfaced at submission time can show the reporter the existing ticket's fix
  status immediately. If the original issue is already resolved or has a documented
  workaround, the reporter gets an answer in seconds instead of waiting for a fresh triage
  cycle.
* On long-running products, the engineers who understood the original root cause may have
  moved on or forgotten the details. The old ticket still holds that context, but only if
  someone finds it. Automated similarity search keeps that institutional knowledge
  reachable instead of letting it age out of search results.
* As the backlog grows from hundreds to tens of thousands of issues, the odds that any
  given new report is an undetected duplicate increase, while manual search gets less
  reliable at the same time. The two effects compound, which is the core argument for
  catching duplicates with a similarity model rather than relying on triager memory or
  keyword search.
* A cluster of related-but-not-identical issues in one component is itself a signal.
  Several reports converging on the same area of the product, even when none of them are
  exact duplicates, often points to a weak spot worth a root-cause fix or a documentation
  gap, which is the reasoning behind the Similarity Analysis and Documentation Gap Finder
  use cases below.
* A spike in duplicate reports clustered right after a release is a low-effort regression
  signal that existing triage workflows do not surface on their own.

## Core use cases

* Smart Duplicate Detection scans the existing defect database for matches, returning a
  similarity score, affected versions, and fix status so a reporter can add to an existing
  ticket instead of opening a new one.
* Components & Labels Optimization suggests standard, accurate components and labels drawn
  from the canonical list, avoiding the label bloat that builds up in long-lived defect
  databases.
* Similarity Analysis identifies related but non-identical issues so developers can see
  patterns across reports and address root causes instead of patching symptoms one ticket
  at a time.
* Documentation Gap Finder reviews product documentation when it detects a cluster of
  similar but non-identical bugs in one component, and suggests where the docs or man pages
  fall short.
* Narrative Refinement turns a raw observation into a searchable title and a structured
  description with standard sections: Steps to Reproduce, Expected Result, Actual Result,
  and Environment Context.

## Workflow

1. The user types a raw brain dump of what went wrong.
2. The tool synthesizes a professional title and structured description.
3. The tool runs similarity analysis and duplicate detection against the refined text,
   which is more accurate once the wording is clean.
4. The tool suggests labels and components from the canonical list.
5. The user reviews the draft, a non-duplicate ticket with clean structure, and decides
   whether to submit it.

## Running locally

Prerequisites: Ollama installed and running with `qwen2.5:7b-instruct` and
`nomic-embed-text` pulled (see [learning.md](learning.md)), and the Python virtual
environment created with the packages in `requirements.txt` installed.

### Start the server

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --reload-dir app --port 8000
```

The `--reload-dir app` flag matters. Without it, uvicorn watches the entire project folder
for changes, including `.venv`. Since `.venv` holds tens of thousands of package files, any
`pip install` triggers an unnecessary, sometimes crash-prone reload. Scoping the watch to
`app` avoids that.

Once it starts, you'll see a line like this, and the server keeps running until you press
Ctrl+C in that terminal:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### Send it a request

The simplest way, no extra tools needed, is to open
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in a browser. FastAPI generates an
interactive page there listing every endpoint. Expand `POST /api/refine`, click "Try it
out", paste a brain dump into the `brain_dump` field, and click "Execute" to see the
structured response.

From a terminal instead:

```powershell
$body = @{ brain_dump = "App crashes when I click export after upgrading to version 4.2" } | ConvertTo-Json
Invoke-RestMethod -Uri http://127.0.0.1:8000/api/refine -Method Post -Body $body -ContentType "application/json"
```

To confirm the server is alive without sending a full request:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```
## Status

Narrative Refinement is implemented and working end to end (`POST /api/refine`). The
remaining use cases, duplicate detection, components and labels suggestion, similarity
analysis, and documentation gap finding, are not yet built. See
[.github/copilot-instructions.md](.github/copilot-instructions.md) for architecture
decisions and open items, and [learning.md](learning.md) for notes on the local model
setup.
