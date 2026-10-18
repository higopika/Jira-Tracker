# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# A "schema" is just a description of exactly what shape a piece of data
# should have. This file describes what a correctly structured bug report
# looks like, so the app can double-check the model's answer before trusting
# it.
#
# WHAT'S DEFINED HERE
#   - BugReportDraft (a class): the five fields a structured bug report must
#     have.
#
# WHO CALLS THIS FILE
#   - app/routers/narrative.py uses it to check the model's answer is well
#     formed, and to describe the shape of what /api/refine returns.
#   - app/routers/duplicates.py uses it to describe what /api/duplicates
#     expects to receive.
# -----------------------------------------------------------------------------

# BaseModel is pydantic's building block for describing a data shape. Field
# lets us give a field a safe default value, like an empty list.
from pydantic import BaseModel, Field


# "class BugReportDraft(BaseModel):" means this class gets pydantic's
# automatic checking for free. If something hands this class a value where
# "title" is a number instead of text, pydantic raises an error right away
# instead of letting bad data slip through quietly.
class BugReportDraft(BaseModel):
    """Structured bug report produced by narrative refinement."""

    title: str  # Required: every draft must have a title, no default value given
    steps_to_reproduce: list[str] = Field(default_factory=list)  # A list of short strings
    expected_result: str = ""
    actual_result: str = ""
    environment_context: str = ""
