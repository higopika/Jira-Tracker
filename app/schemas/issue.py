# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This file describes the shape of the answer that POST /api/duplicates
# sends back: a list of existing issues that might match a new report, each
# with a similarity score.
#
# WHAT'S DEFINED HERE
#   - DuplicateMatch (a class): one existing issue that might be a match.
#   - DuplicateCheckResponse (a class): a list of DuplicateMatch results,
#     wrapped together as one answer.
#
# WHO CALLS THIS FILE
#   - app/services/similarity.py builds these objects after comparing a new
#     report against everything stored in the database.
#   - app/routers/duplicates.py uses DuplicateCheckResponse to describe what
#     the endpoint sends back.
# -----------------------------------------------------------------------------
from pydantic import BaseModel, Field


class DuplicateMatch(BaseModel):
    """A candidate existing issue that may match a newly reported bug."""

    issue_id: int
    title: str
    similarity_score: float  # How close this match is: 1.0 means identical, 0.0 means unrelated
    status: str  # For example "open" or "fixed", taken from the stored issue
    affected_versions: list[str] = Field(default_factory=list)
    likely_duplicate: bool  # True once similarity_score passes the configured threshold


# One response can include several matches, so this class is just a wrapper
# holding a list of the DuplicateMatch objects described above.
class DuplicateCheckResponse(BaseModel):
    """The ranked list of existing issues closest to a new report."""

    matches: list[DuplicateMatch] = Field(default_factory=list)
