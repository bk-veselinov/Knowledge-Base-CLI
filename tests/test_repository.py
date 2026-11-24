from pathlib import Path

import pytest

from knowledge.errors import StorageError
from knowledge.repository import SqliteRepository


def test_add_and_get_item(repo: SqliteRepository) -> None:
    item = repo.add("Test Title", "Test Content")
    retrieved_item = repo.get(item.id)

    assert retrieved_item is not None
    assert retrieved_item.id == item.id

def test_get_none_for_nonexistent_item(repo: SqliteRepository) -> None:
    assert repo.get(1000) is None

def test_list_all_items(repo: SqliteRepository) -> None:
    repo.add("Title 1", "Content 1")
    repo.add("Title 2", "Content 2")

    items = repo.list_all()
    assert len(items) == 2

def test_list_all_items_sorted_by_id(repo: SqliteRepository) -> None:
    item1 = repo.add("2B", "2B Content")
    item2 = repo.add("1A", "1A Content")

    items = repo.list_all()
    assert items[0].id == item1.id
    assert items[1].id == item2.id

def test_delete_item(repo: SqliteRepository) -> None:
    item = repo.add("Title to Delete", "Content to Delete")
    deleted = repo.delete(item.id)

    assert deleted is True
    assert repo.get(item.id) is None

def test_delete_nonexistent_item(repo: SqliteRepository) -> None:
    deleted = repo.delete(1000)
    assert deleted is False

def test_deleted_id_cannot_be_reused(repo: SqliteRepository) -> None:
    item = repo.add("Title", "Content")
    repo.delete(item.id)
    new_item = repo.add("New Title", "New Content")

    assert new_item.id != item.id

def test_corrupted_file_raises_storage_error(db_path: Path) -> None:
    db_path.write_text("this is not a database")

    with pytest.raises(StorageError, match="corrupted"):
        SqliteRepository(db_path)

def test_missing_parent_folder_is_created(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "folder" / "kb.db"

    SqliteRepository(db_path)

    assert db_path.exists()