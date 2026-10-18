# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This is the only file allowed to talk to Ollama (the local model) directly.
# Every feature in the app goes through the one object at the bottom of this
# file instead of calling Ollama's web address themselves.
#
# WHAT'S DEFINED HERE
#   - OllamaClient (a class): a blueprint describing how to send text to
#     Ollama and get an answer back, either a written JSON answer or a list
#     of numbers (an embedding).
#   - ollama_client (an object): the one actual OllamaClient that every other
#     file reuses.
#
# WHO CALLS THIS FILE
#   - app/routers/narrative.py calls ollama_client.generate_json() to turn a
#     brain dump into a structured draft.
#   - app/routers/duplicates.py and scripts/seed_db.py call
#     ollama_client.embed() to turn text into a list of numbers for
#     similarity search.
#
# STEP BY STEP, FOR generate_json()
#   1. Package up the model name, instructions, and user text as one request.
#   2. Send it to Ollama's /api/generate web address and wait for a reply.
#   3. Ollama replies with text that looks like JSON; turn that text into a
#      real Python dictionary and return it.
# -----------------------------------------------------------------------------

import json
from typing import Any

# httpx is a library for making HTTP requests (the same kind of request a
# web browser makes), used here to call Ollama's local web API.
import httpx

from app.config import settings


# A class is a blueprint for building objects that all work the same way.
# This blueprint describes one thing: "an object that knows the address of
# an Ollama server and can send it requests."
class OllamaClient:
    """Thin wrapper around the local Ollama API.

    Isolates the rest of the app from the specific local LLM runtime so the
    underlying backend (Ollama, llama.cpp, vLLM, ...) can be swapped later
    without touching feature code.
    """

    # __init__ runs automatically every time a new OllamaClient object gets
    # built from this blueprint. "self" means "this particular object", and
    # "self._host = host" saves the server address onto that object so the
    # methods below can use it later.
    def __init__(self, host: str = settings.ollama_host) -> None:
        self._host = host

   # A method is a function that belongs to a class and can use "self" to
    # get at the object's own saved data (here, self._host). The "*" means
    # every argument after it must be given by name, like
    # generate_json(model=..., system=..., prompt=...), which prevents mixing
    # up the order by accident.
    def generate_json(self, *, model: str, system: str, prompt: str) -> dict[str, Any]:
        """Call the model and parse its response as JSON.

        Raises httpx.HTTPStatusError if the Ollama request fails, and
        json.JSONDecodeError if the model's response is not valid JSON.
        """
        # httpx.post sends an HTTP POST request, the same kind a web form
        # submission uses, to Ollama's /api/generate endpoint, with the
        # model name, instructions, and the user's text packed as JSON.
         # Send a request to Ollama, similar to submitting a web form, asking
        # it to generate a reply using the given model, instructions, and
        # user text.
        response = httpx.post(
            f"{self._host}/api/generate",
            json={
                "model": model,
                "system": system,
                "prompt": prompt,
                "format": "json",
                "stream": False,
            },
            timeout=120.0,
        )
        # If Ollama responded with an error status code (4xx/5xx), this
        # raises an exception instead of silently continuing with bad data.
        response.raise_for_status()
        raw_text = response.json()["response"]
        # The model's answer arrives as plain text that happens to look like
        # JSON. json.loads() turns that text into a real Python dictionary.
        return json.loads(raw_text)

    def embed(self, *, model: str, text: str) -> list[float]:
        """Call an embedding model and return the resulting vector.

        Used to turn a bug report's text into a list of numbers that can be
        compared against other reports for similarity, rather than for
        generating a written response.
        """
        response = httpx.post(
            f"{self._host}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["embedding"]


# This line builds one real OllamaClient object, right now, the first time
# this file is imported, and saves it as "ollama_client". Every other file
# writes "from app.llm.client import ollama_client" to reuse this exact
# object instead of building a new one.
ollama_client = OllamaClient()
