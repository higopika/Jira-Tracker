# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This is the starting point of the whole application. When you run the
# server, this is the first file it looks at.
#
# WHAT'S DEFINED HERE
#   - lifespan (a function): runs once when the server turns on, and would
#     run again when it turns off.
#   - app (an object): the running web server itself. Every endpoint in the
#     project eventually connects back to this one object.
#   - health (a function): answers a simple "are you alive?" check.
#
# WHO CALLS THIS FILE
#   - Nobody imports main.py. Instead, a command tells uvicorn to run it
#     directly: "uvicorn app.main:app".
#
# STEP BY STEP, WHEN THE SERVER STARTS
#   1. uvicorn loads this file and finds the "app" object below.
#   2. Before accepting any requests, it runs lifespan(), which calls
#      init_db() to make sure the database table exists.
#   3. The server is now ready. Every request for /api/refine or
#      /api/duplicates gets routed to the matching function in
#      narrative.py or duplicates.py.
# -----------------------------------------------------------------------------

# asynccontextmanager turns a regular function into something FastAPI can
# run once at startup and once at shutdown (see lifespan() below).
# asynccontextmanager lets us write a function (lifespan, below) that FastAPI
# runs in two parts: everything before the word "yield" happens at startup,
# everything after it would happen at shutdown.
from contextlib import asynccontextmanager
from typing import AsyncIterator

# FastAPI is the web framework class. Creating an instance of it (see
# "app = FastAPI(...)" below) gives you an object that knows how to turn
# incoming web requests into Python function calls, and Python return values
# back into web responses.
from fastapi import FastAPI

from app.db import init_db

# Each router groups related endpoints into one file. Importing them here and
# attaching them below is what makes /api/refine and /api/duplicates actually
# work.
from app.routers.duplicates import router as duplicates_router
from app.routers.narrative import router as narrative_router


# This function runs exactly once when the server starts (everything before
# "yield") and once when the server shuts down (anything after "yield",
# there's nothing here, but it's where cleanup code would go). FastAPI calls
# this automatically because we pass it in as "lifespan=lifespan" below.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()  # Make sure the issues table exists before the first request arrives
    yield


# This single line creates the actual running application. Everything else
# in this file attaches to this one object.
app = FastAPI(title="Jira Issue Architect", lifespan=lifespan)
app.include_router(narrative_router, prefix="/api", tags=["narrative"])
app.include_router(duplicates_router, prefix="/api", tags=["duplicates"])


# "@app.get(\"/health\")" means: whenever someone visits /health, or any
# program sends a GET request there, run this function and send back
# whatever it returns. You don't call health() yourself.
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
