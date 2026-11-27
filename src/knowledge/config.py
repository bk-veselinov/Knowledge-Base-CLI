import os
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / "knowledge" / "knowledge.db"


def get_database_path() -> Path:
    """Returns the database path, using the environment variable if set, otherwise the default path."""
    env_db_path = os.getenv("DB_PATH", "").strip()
    return Path(env_db_path).expanduser() if env_db_path else DEFAULT_DB_PATH
