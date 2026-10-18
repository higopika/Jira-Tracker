# Jira Issue Architect — Project Guidelines

## Project Overview

Jira Issue Architect is a bug-reporting assistant. A user pastes a raw "brain dump" of an
observed bug; the tool synthesizes a clean title and structured description, checks it
against the existing defect database for duplicates and related issues, suggests
components/labels from a user-provided canonical list, and presents a draft report for the
user to review and submit. The tool never auto-submits — the human always reviews the
final draft.

Core use cases (see problem statement for full detail): Smart Duplicate Detection,
Components & Labels Optimization, Similarity Analysis, Documentation Gap Finder, Narrative
Refinement.

## Architecture

- **Backend**: Python + FastAPI. Exposes endpoints for: narrative refinement, duplicate
  search, similarity analysis, label/component suggestion, and draft submission.
- **Frontend**: Simple server-rendered or lightweight web UI consumed by the FastAPI app —
  keep it minimal; this is not a SPA-heavy project.
- **Storage**: Local SQLite file for the defect/issue database and any cached embeddings.
  Do not introduce a different database engine without discussion.
- **LLM inference**: Must run on a **local/open-source model only**. No bug content, Jira
  dumps, or product documentation may ever be sent to a hosted/third-party LLM API — this is
  a hard privacy constraint, not a preference. The specific local runtime (e.g. Ollama,
  llama.cpp, vLLM) is not yet chosen, so:
  - Isolate all model calls behind a single interface/module (e.g. `llm/client.py`) so the
    underlying runtime can be swapped without touching feature code.
  - Do not hardcode a runtime's SDK calls directly into feature logic.
- **Context sources** fed to the model: the Jira/defect dump, product documentation, and a
  user-supplied sanitized list of canonical component names and labels (used to keep
  suggestions consistent and avoid label bloat).

## Conventions

- Use type hints on all new Python functions and Pydantic models for request/response
  schemas.
- Keep PII/sensitive-data sanitization as an explicit, testable step before any text is
  passed to the LLM or stored — do not inline sanitization logic ad hoc across call sites.
- Any feature that produces a "suggestion" (duplicate, label, component, doc gap) must
  return a confidence/similarity score alongside the suggestion — never present a bare
  guess as fact.
- Draft bug reports are structured output (e.g. a typed model with Title, Steps to
  Reproduce, Expected Result, Actual Result, Environment Context) — avoid passing around
  unstructured strings between pipeline stages once the narrative is synthesized.

## Build and Test

Not yet established — this project has no code yet. Once scaffolded, this section should
be updated with the actual install/run/test commands (expected: `pip install -r
requirements.txt`, `uvicorn` entrypoint, `pytest`).
