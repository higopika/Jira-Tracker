# -----------------------------------------------------------------------------
# WHAT THIS FILE IS FOR
# -----------------------------------------------------------------------------
# This is the settings file. It holds every value the app might need to
# change later, like the model name or where the database file lives, all
# in one place.
#
# WHAT'S DEFINED HERE
#   - Settings (a class): a list of setting names and their default values.
#   - settings (an object): the one copy of Settings that every other file
#     actually uses.
#
# WHO USES THIS FILE
#   - Every other file in app/ writes "from app.config import settings" to
#     read a value, for example settings.generation_model.
#
# STEP BY STEP
#   1. Python reads this file once, the first time the app starts.
#   2. "settings = Settings()" runs, creating the one settings object.
#   3. From then on, every other file reuses that same object.
# -----------------------------------------------------------------------------

# BaseSettings is a ready-made class from the pydantic-settings library. A
# plain Python class just stores values as given. BaseSettings does one extra
# thing: it checks for matching environment variables and uses those instead
# of the defaults below, if any are set.
from pydantic_settings import BaseSettings


# "class Settings(BaseSettings):" defines a new class named Settings that
# inherits all the environment-variable-reading behavior from BaseSettings.
# Each line below is a "field": a name, a type (str, float, ...), and a
# default value used when no environment variable overrides it.
class Settings(BaseSettings):
    """Runtime configuration, overridable via environment variables."""

    ollama_host: str = "http://localhost:11434"  # Where the local Ollama server listens
    generation_model: str = "qwen2.5:7b-instruct"  # Model used for writing/structuring text
    embedding_model: str = "nomic-embed-text"  # Model used for similarity/duplicate search
    db_path: str = "data/defects.db"  # Where the SQLite database file is stored on disk
    duplicate_similarity_threshold: float = 0.85  # Score above which a match counts as a duplicate


# This line creates one actual object (an "instance") of the Settings class
# described above. Every other file in the app imports this one object
# ("from app.config import settings") instead of creating its own, so
# everyone reads the exact same configuration values.
settings = Settings()
