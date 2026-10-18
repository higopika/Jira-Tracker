# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This file defines the POST /api/duplicates web address: given a draft bug
# report that's already been structured, it checks whether anything similar
# already exists in the local database.
#
# WHAT'S DEFINED HERE
#   - _build_search_text (a function): squashes a draft's fields into one
#     block of text to compare against other issues.
#   - check_duplicates (a function): does the actual work, called
#     automatically by FastAPI.
#
# WHO CALLS THIS FILE
#   - app/main.py attaches "router" from here to the running server.
#   - FastAPI calls check_duplicates() whenever a POST request to
#     /api/duplicates arrives.
#
# STEP BY STEP, WHEN A REQUEST ARRIVES
#   1. FastAPI reads the incoming JSON and builds a BugReportDraft object.
#   2. _build_search_text() combines its fields into one piece of text.
#   3. ollama_client.embed() turns that text into a list of numbers.
#   4. find_duplicates() (in services/similarity.py) compares those numbers
#      against every issue already stored, and returns the closest matches.
# -----------------------------------------------------------------------------

from fastapi import APIRouter

from app.config import settings
from app.llm.client import ollama_client
from app.schemas.bug_report import BugReportDraft
from app.schemas.issue import DuplicateCheckResponse
from app.services.similarity import find_duplicates

router = APIRouter()


def _build_search_text(draft: BugReportDraft) -> str:
    """Combine every field of a draft into one block of text to embed."""
    # The leading underscore in "_build_search_text" is a Python convention
    # meaning "internal helper, not meant to be imported and used by other
    # files", unlike check_duplicates below which other code is meant to
    # call indirectly through the web endpoint.
    return "\n".join(
        [
            draft.title,
            " ".join(draft.steps_to_reproduce),
            draft.expected_result,
            draft.actual_result,
            draft.environment_context,
        ]
    )


# This decorator registers check_duplicates() as the handler for POST
# /api/duplicates. FastAPI turns the incoming JSON straight into a
# BugReportDraft object before calling this function.
@router.post("/duplicates", response_model=DuplicateCheckResponse)
def check_duplicates(draft: BugReportDraft) -> DuplicateCheckResponse:
    """Find existing issues similar to a refined bug report draft.

    Takes the same structured draft that /api/refine produces, so the
    workflow is: refine the brain dump first, then check the clean result
    for duplicates.
    """
    search_text = _build_search_text(draft)
    # Turn the draft's text into a list of numbers (a vector) using the
    # embedding model, through the same shared Ollama client used elsewhere.
    embedding = ollama_client.embed(model=settings.embedding_model, text=search_text)
    # Hand that list of numbers to similarity.py, which compares it against
    # every issue already in the database and returns the closest ones.
    return find_duplicates(embedding)
