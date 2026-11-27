from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from knowledge.manager import KnowledgeManager
from knowledge.repository import SqliteRepository


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest.fixture
def repo(db_path: Path) -> SqliteRepository:
    return SqliteRepository(db_path)


@pytest.fixture
def manager(repo: SqliteRepository) -> KnowledgeManager:
    return KnowledgeManager(repo)


@pytest.fixture
def mock_manager(mocker: MockerFixture) -> MagicMock:
    mock = mocker.create_autospec(KnowledgeManager, instance=True)
    mocker.patch("knowledge.cli._knowledge_manager", return_value=mock)
    return mock
