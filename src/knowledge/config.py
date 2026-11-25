import os
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", Path(__file__).parent.parent / "knowledge.db")
DEFAULT_DB_PATH = Path.home() / "knowledge" / "knowledge.db"

def get_database_path() -> Path:
    """Returns the database path, using the environment variable if set, otherwise the default path."""
    return Path(DB_PATH) if DB_PATH else DEFAULT_DB_PATH