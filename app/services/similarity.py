# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This file does the actual math behind duplicate detection: given a new
# report's list of numbers (its embedding), work out which stored issues are
# the closest match.
#
# WHAT'S DEFINED HERE
#   - cosine_similarity (a function): compares two lists of numbers and
#     returns how alike they are, from 0 (unrelated) to 1 (identical).
#   - find_duplicates (a function): loads every stored issue, scores each
#     one against the new report, and returns the best matches.
#
# WHO CALLS THIS FILE
#   - app/routers/duplicates.py calls find_duplicates() after turning a
#     draft into an embedding.
#
# STEP BY STEP
#   1. find_duplicates() asks app/db.py for every stored issue's saved
#      embedding.
#   2. Each one gets compared to the new report's embedding using
#      cosine_similarity().
#   3. Results get sorted so the closest match comes first, and only the top
#      few are kept and returned.
# -----------------------------------------------------------------------------

import json
import math

from app.config import settings
from app.db import get_connection
from app.schemas.issue import DuplicateCheckResponse, DuplicateMatch


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Return how closely two embedding vectors point in the same direction.

    1.0 means identical direction (very similar text), 0.0 means unrelated.
    """
    # "zip(a, b)" pairs up each number in list a with the number in the same
    # spot in list b. Multiplying each pair and adding up the results is a
    # standard way (called a "dot product") to measure how aligned two
    # lists of numbers are.
    dot = sum(x * y for x, y in zip(a, b))
    # These two lines measure the "length" of each list of numbers, used
    # below to turn the dot product into a score between -1 and 1 regardless
    # of how large the raw numbers are.
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def find_duplicates(embedding: list[float], top_n: int = 3) -> DuplicateCheckResponse:
    """Compare an embedding against every stored issue and return the closest matches.

    This loads every issue's embedding into memory and scores it against the
    query. That's fine for a learning project with a handful of seed issues;
    a real defect database with thousands of issues would need a vector index
    instead of scanning every row on every request.
    """
    # Open a connection to the database (see app/db.py) and read back every
    # stored issue's basic details plus its saved embedding.
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, status, affected_versions, embedding FROM issues"
        ).fetchall()

    # Build a plain list where each entry is one issue's details plus a
    # freshly calculated similarity score. Embeddings and affected_versions
    # are stored as plain text in the database, so json.loads() turns that
    # text back into a real Python list here.
    scored = [
        (
            row[0],
            row[1],
            row[2],
            json.loads(row[3]) if row[3] else [],
            cosine_similarity(embedding, json.loads(row[4])),
        )
        for row in rows
    ]
    # Put the most similar issue (highest score) first.
    scored.sort(key=lambda item: item[4], reverse=True)

    # Keep only the top few matches and turn each one into a proper
    # DuplicateMatch object, ready to be sent back as a clean response.
    matches = [
        DuplicateMatch(
            issue_id=issue_id,
            title=title,
            similarity_score=round(score, 4),
            status=status,
            affected_versions=affected_versions,
            likely_duplicate=score >= settings.duplicate_similarity_threshold,
        )
        for issue_id, title, status, affected_versions, score in scored[:top_n]
    ]
    return DuplicateCheckResponse(matches=matches)
