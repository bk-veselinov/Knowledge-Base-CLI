"""SQLite storage"""

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from knowledge.errors import StorageError
from knowledge.models import KnowledgeItem

_SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL CHECK (length(trim(title)) > 0),
    content    TEXT NOT NULL CHECK (length(trim(content)) > 0),
    created_at TEXT NOT NULL
);
"""


class SqliteRepository:
    """SQLite storage for knowledge items."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize_database()

    def get(self, item_id: int) -> KnowledgeItem | None:
        """Get a knowledge item by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, content, created_at FROM items WHERE id = ?",
                (item_id,),
            )
            row = cursor.fetchone()
            return self._row_to_knowledge_item(row) if row else None

    def list_all(self) -> list[KnowledgeItem]:
        """List all knowledge items."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT id, title, content, created_at FROM items ORDER BY id"
            )
            rows = cursor.fetchall()

            return [self._row_to_knowledge_item(row) for row in rows]

    def add(self, title: str, content: str) -> KnowledgeItem:
        """Add a new knowledge item."""
        created_at = datetime.now(UTC)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO items (title, content, created_at) VALUES (?, ?, ?)",
                (title, content, created_at.isoformat()),
            )
            item_id = cursor.lastrowid
            return KnowledgeItem(item_id, title, content, created_at)

    def delete(self, item_id: int) -> bool:
        """Delete a knowledge item by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
            return cursor.rowcount > 0

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

        except (OSError, sqlite3.Error) as e:
            raise StorageError(f"The file {self.db_path} could not be opened: {e}")

        try:
            with conn:
                yield conn

        except sqlite3.OperationalError as e:
            raise StorageError(f"Cannot access {self.db_path} file: {e}")

        except sqlite3.DatabaseError as e:
            raise StorageError(
                f"The file {self.db_path} is corrupted or is not a valid database: {e}"
            )

        finally:
            conn.close()

    def _initialize_database(self) -> None:
        with self._get_connection() as conn:
            conn.executescript(_SCHEMA)

    @staticmethod
    def _row_to_knowledge_item(row: sqlite3.Row) -> KnowledgeItem:
        return KnowledgeItem(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]).replace(tzinfo=UTC),
        )
