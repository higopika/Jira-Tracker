# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This is the only file that knows how to open the SQLite database file and
# set up its table. Every other file that needs to read or write issues goes
# through get_connection(), defined here.
#
# WHAT'S DEFINED HERE
#   - init_db (a function): creates the "issues" table if it isn't there yet.
#   - get_connection (a function): opens a connection to the database file
#     and closes it automatically when you're done.
#
# WHO CALLS THIS FILE
#   - app/main.py calls init_db() once, when the server starts.
#   - app/services/similarity.py calls get_connection() to read issues.
#   - scripts/seed_db.py calls both, to set up and fill the database.
#
# STEP BY STEP
#   1. init_db() checks the database file's folder exists, then makes sure
#      the "issues" table exists.
#   2. Any code that needs to read or write data opens get_connection(),
#      does its work, and the connection closes automatically afterward.
# -----------------------------------------------------------------------------

import sqlite3

# contextmanager lets us write a function that works with Python's
# "with ... as ...:" syntax (see get_connection below), so a database
# connection always gets closed, even if something goes wrong partway
# through.
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.config import settings


def init_db() -> None:
    """Create the issues table if it doesn't already exist."""
    # Make sure the folder the database file lives in actually exists first
    # (SQLite won't create missing folders for you, only the file itself).
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        # "CREATE TABLE IF NOT EXISTS" is plain SQL. conn.execute(...) sends
        # that SQL text straight to SQLite. This only has an effect the
        # first time the app runs; after that the table already exists and
        # this line does nothing.
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                search_text TEXT NOT NULL,
                component TEXT,
                labels TEXT,
                status TEXT NOT NULL DEFAULT 'open',
                affected_versions TEXT,
                embedding TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()  # Writes the change to disk; without this nothing is actually saved


# "@contextmanager" turns this generator function into something you can use as
# "with get_connection() as conn:" elsewhere in the app. Whatever is before
# "yield" runs when the "with" block starts; whatever is after it (closing
# the connection) runs automatically when the block ends, even if an error
# happened in between.
@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(settings.db_path)
    try:
        yield conn
    finally:
        conn.close()
