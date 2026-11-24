from pathlib import Path

import pytest

from knowledge.repository import SqliteRepository
from knowledge.manager import KnowledgeManager



@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def repo(db_path: Path) -> SqliteRepository:
    return SqliteRepository(db_path)

@pytest.fixture
def manager(repo: SqliteRepository) -> KnowledgeManager:
    return KnowledgeManager(repo)