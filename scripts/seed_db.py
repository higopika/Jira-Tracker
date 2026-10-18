"""Seed the local defect database with example issues for testing duplicate detection.

-----------------------------------------------------------------------------
WHAT THIS FILE IS FOR
-----------------------------------------------------------------------------
This is a standalone script, not part of the running web server. You run it
once (or whenever you want to reset to known test data) directly from a
terminal, to fill the database with a few example bug reports so there's
something real to test duplicate detection against.

WHAT'S DEFINED HERE
  - SEED_ISSUES: a plain list of example bug reports to insert.
  - seed (a function): does the actual work of inserting them.

WHO CALLS THIS FILE
  - Nobody imports this file from elsewhere. You run it directly:

        .venv\\Scripts\\python.exe -m scripts.seed_db

STEP BY STEP
  1. init_db() makes sure the issues table exists.
  2. If the table already has rows, stop here to avoid duplicate inserts.
  3. For each example issue, ask Ollama to turn its text into a list of
     numbers (an embedding), then insert it into the database.
-----------------------------------------------------------------------------
"""

import json

from app.config import settings
from app.db import get_connection, init_db
from app.llm.client import ollama_client

# A plain list of dictionaries. Each dictionary is one example bug report
# that will be inserted into the database.
SEED_ISSUES = [
    {
        "title": "Export crashes the application on Windows after upgrading to 4.2",
        "component": "Export",
        "labels": "crash,regression",
        "status": "fixed",
        "affected_versions": ["4.2"],
        "search_text": (
            "Export crashes the application on Windows after upgrading to 4.2\n"
            "Upgrade to version 4.2. Click export. Application crashes immediately.\n"
            "Expected: export completes successfully.\n"
            "Actual: application crashes.\n"
            "Windows 11, laptop."
        ),
    },
    {
        "title": "UI freezes when saving large documents",
        "component": "Editor",
        "labels": "performance",
        "status": "open",
        "affected_versions": ["4.0", "4.1"],
        "search_text": (
            "UI freezes when saving large documents\n"
            "Open a document over 50MB. Click save. UI becomes unresponsive for 30+ seconds.\n"
            "Expected: save completes quickly without freezing the UI.\n"
            "Actual: UI freezes during save.\n"
            "Windows 10 and 11, desktop."
        ),
    },
    {
        "title": "Login fails intermittently with expired token error",
        "component": "Auth",
        "labels": "auth,intermittent",
        "status": "open",
        "affected_versions": ["4.1", "4.2"],
        "search_text": (
            "Login fails intermittently with expired token error\n"
            "Log in normally. Occasionally see a 'token expired' error on the first attempt.\n"
            "Expected: login succeeds consistently.\n"
            "Actual: intermittent token expired errors requiring a retry.\n"
            "macOS and Windows."
        ),
    },
]


def seed() -> None:
    init_db()  # Make sure the issues table exists before inserting anything
    with get_connection() as conn:
        # Check whether the table already has data before inserting again,
        # so running this script a second time doesn't create duplicate
        # copies of the same seed issues.
        existing = conn.execute("SELECT COUNT(*) FROM issues").fetchone()[0]
        if existing > 0:
            print(f"Database already has {existing} issues, skipping seed.")
            return

        # Loop over every example issue defined above, one at a time.
        for issue in SEED_ISSUES:
            # Ask Ollama's embedding model to turn this issue's text into a
            # list of numbers, the same way a real new bug report would be
            # embedded when checked for duplicates later.
            embedding = ollama_client.embed(
                model=settings.embedding_model, text=issue["search_text"]
            )
            # Insert one new row into the issues table. The "?" marks are
            # placeholders that get safely filled in with the tuple of
            # values below, which avoids SQL injection problems that can
            # happen when building SQL strings by hand.
            conn.execute(
                """
                INSERT INTO issues
                    (title, search_text, component, labels, status, affected_versions, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    issue["title"],
                    issue["search_text"],
                    issue["component"],
                    issue["labels"],
                    issue["status"],
                    json.dumps(issue["affected_versions"]),
                    json.dumps(embedding),
                ),
            )
        conn.commit()  # Actually save all the inserts above to disk
    print(f"Seeded {len(SEED_ISSUES)} issues into {settings.db_path}")


# This check means "only run seed() if this file was launched directly
# (python -m scripts.seed_db), not if some other file imports it". It's a
# standard Python pattern for files that can be both run as a script and
# safely imported elsewhere.
if __name__ == "__main__":
    seed()
