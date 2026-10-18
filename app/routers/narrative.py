# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This file defines the POST /api/refine web address: the one a user (or the
# interactive docs page) calls to turn a raw brain dump into a clean,
# structured draft.
#
# WHAT'S DEFINED HERE
#   - RefineRequest (a class): the shape of what the caller must send in
#     (just one field, brain_dump).
#   - refine_narrative (a function): does the actual work, called
#     automatically by FastAPI, never called directly by other code.
#
# WHO CALLS THIS FILE
#   - app/main.py imports "router" from here and attaches it to the running
#     server.
#   - FastAPI itself calls refine_narrative() whenever a POST request to
#     /api/refine arrives.
#
# STEP BY STEP, WHEN A REQUEST ARRIVES
#   1. FastAPI reads the incoming JSON and builds a RefineRequest object.
#   2. refine_narrative() sends request.brain_dump to ollama_client, along
#      with the instructions from narrative_refinement.py.
#   3. The model's answer gets checked against BugReportDraft's shape.
#   4. If it matches, that structured draft is sent back as the response.
#      If not, a clear error is sent back instead.
# -----------------------------------------------------------------------------

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.llm.client import ollama_client
from app.prompts.narrative_refinement import NARRATIVE_REFINEMENT_SYSTEM_PROMPT
from app.schemas.bug_report import BugReportDraft

# APIRouter is a mini, standalone version of the FastAPI app, used so each
# feature's endpoints can live in their own file. app/main.py later attaches
# this router to the real running server with app.include_router(...).
router = APIRouter()


# This defines the exact shape of data this endpoint expects to receive in
# the request body. FastAPI reads this class and automatically rejects any
# request that doesn't include a "brain_dump" text field.
class RefineRequest(BaseModel):
    brain_dump: str


# The line above this function is a decorator. It tells FastAPI: "whenever a
# POST request arrives at /refine (which becomes /api/refine once main.py
# adds the /api prefix), run this function and send back whatever it
# returns." You never call refine_narrative() yourself; FastAPI does.
@router.post("/refine", response_model=BugReportDraft)
def refine_narrative(request: RefineRequest) -> BugReportDraft:
    # Ask the shared Ollama client to send the brain dump to the model,
    # along with the formatting instructions, and hand back a plain Python
    # dictionary.
    raw = ollama_client.generate_json(
        model=settings.generation_model,
        system=NARRATIVE_REFINEMENT_SYSTEM_PROMPT,
        prompt=request.brain_dump,
    )
    try:
        # model_validate checks the dictionary actually has the right fields
        # in the right shape, and builds a real BugReportDraft object from
        # it.
        return BugReportDraft.model_validate(raw)
    except ValidationError as exc:
        # If the model's answer didn't match the expected shape, send back a
        # clear error instead of passing along broken data. HTTPException is
        # FastAPI's way of returning a specific error status (502 here) with
        # a message explaining what went wrong.
        raise HTTPException(
            status_code=502,
            detail=f"Model returned output that did not match the expected schema: {exc}",
        ) from exc
