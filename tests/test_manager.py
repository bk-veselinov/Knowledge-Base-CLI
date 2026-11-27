import pytest

from knowledge.errors import InvalidInputError, ItemNotFoundError
from knowledge.manager import TITLE_MAX_LENGTH, KnowledgeManager


def test_trim_title_and_content(manager: KnowledgeManager) -> None:
    item = manager.add_item("  Title  ", "  Content  ")

    assert item.title == "Title"
    assert item.content == "Content"

@pytest.mark.parametrize("title", ["", "   ", "\n\t\r"])
def test_empty_title_raises(manager: KnowledgeManager, title: str) -> None:
    with pytest.raises(InvalidInputError, match="Title cannot be empty."):
        manager.add_item(title, "Content")

@pytest.mark.parametrize("content", ["", "   ", "\n\t\r"])
def test_empty_content_raises(manager: KnowledgeManager, content: str) -> None:
    with pytest.raises(InvalidInputError, match="Content cannot be empty."):
        manager.add_item("Title", content)

def test_title_too_long_raises(manager: KnowledgeManager) -> None:
    long_title = "A" * (TITLE_MAX_LENGTH + 1)

    with pytest.raises(InvalidInputError, match=f"Title cannot exceed {TITLE_MAX_LENGTH} characters."):
        manager.add_item(long_title, "Content")

def test_title_at_max_length_is_valid(manager: KnowledgeManager) -> None:
    max_length_title = "A" * TITLE_MAX_LENGTH

    item = manager.add_item(max_length_title, "Content")

    assert item.title == max_length_title

def test_get_nonexistent_item_raises(manager: KnowledgeManager) -> None:
    with pytest.raises(ItemNotFoundError, match="No item with ID 1000."):
        manager.get_item(1000)

def test_delete_nonexistent_item_raises(manager: KnowledgeManager) -> None:
    with pytest.raises(ItemNotFoundError, match="No item with ID 1000."):
        manager.delete_item(1000)

def test_delete_item_returns_deleted_item(manager: KnowledgeManager) -> None:
    item = manager.add_item("Title", "Content")
    deleted_item = manager.delete_item(item.id)

    assert deleted_item == item
    with pytest.raises(ItemNotFoundError):
        manager.get_item(item.id)

def test_add_and_get_item(manager: KnowledgeManager) -> None:
    item = manager.add_item("Test Title", "Test Content")
    retrieved_item = manager.get_item(item.id)

    assert retrieved_item is not None
    assert retrieved_item == item

def test_list_items_returns_all_items(manager: KnowledgeManager) -> None:
    item1 = manager.add_item("Title 1", "Content 1")
    item2 = manager.add_item("Title 2", "Content 2")

    items = manager.list_items()

    assert len(items) == 2
    assert items[0] == item1
    assert items[1] == item2

def test_search_items(manager: KnowledgeManager) -> None:
    python_item = manager.add_item("Python basics", "Variables and loops")
    manager.add_item("Cooking", "Pasta recipe")

    results = manager.search_items("python")

    assert [result.knowledge_item for result in results] == [python_item]

@pytest.mark.parametrize("query", ["", "   "])
def test_search_items_empty_query(manager: KnowledgeManager, query: str) -> None:
    with pytest.raises(InvalidInputError, match="Query cannot be empty."):
        manager.search_items(query)

def test_search_items_respects_limit(manager: KnowledgeManager) -> None:
    for i in range(3):
        manager.add_item(f"Python {i}", "Content")

    results = manager.search_items("python", limit=2)

    assert len(results) == 2
