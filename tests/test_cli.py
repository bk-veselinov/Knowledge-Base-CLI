from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from knowledge.cli import app
from knowledge.errors import InvalidInputError, ItemNotFoundError
from knowledge.models import KnowledgeItem, ScoredKnowledgeItem

runner = CliRunner()

def make_item(item_id: int = 1, title: str = "Title", content: str = "Content") -> KnowledgeItem:
    return KnowledgeItem(item_id, title, content, datetime(2026, 11, 26, 20, 0, tzinfo=UTC))



def test_add_valid_input(mock_manager: MagicMock) -> None:
    mock_manager.add_item.return_value = make_item()

    result = runner.invoke(app, ["add", "Title", "Content"])

    assert result.exit_code == 0
    assert "Added item: Title (ID: 1)" in result.output
    mock_manager.add_item.assert_called_once_with("Title", "Content")


def test_add_invalid_input(mock_manager: MagicMock) -> None:
    mock_manager.add_item.side_effect = InvalidInputError("Title cannot be empty.")

    result = runner.invoke(app, ["add", " ", "Content"])

    assert result.exit_code == 2
    assert "Title cannot be empty." in result.output


def test_show_with_valid_id(mock_manager: MagicMock) -> None:
    mock_manager.get_item.return_value = make_item()

    result = runner.invoke(app, ["show", "1"])

    assert result.exit_code == 0
    assert "Title: Title" in result.output
    assert "Content:\nContent" in result.output
    mock_manager.get_item.assert_called_once_with(1)



def test_show_with_nonexistent_id(mock_manager: MagicMock) -> None:
    mock_manager.get_item.side_effect = ItemNotFoundError(76)

    result = runner.invoke(app, ["show", "76"])

    assert result.exit_code == 1
    assert "No item with ID 76." in result.output


@pytest.mark.parametrize("item_id", ["0", "-5", "abc"])
def test_show_with_invalid_id(mock_manager: MagicMock, item_id: str) -> None:
    result = runner.invoke(app, ["show", "--", item_id])

    assert result.exit_code == 2
    mock_manager.get_item.assert_not_called()


def test_list_empty(mock_manager: MagicMock) -> None:
    mock_manager.list_items.return_value = []

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    assert "No knowledge items found." in result.output



def test_list_with_limit(mock_manager: MagicMock) -> None:
    mock_manager.list_items.return_value = [make_item(i, f"Item {i}") for i in range(1, 4)]

    result = runner.invoke(app, ["list", "--limit", "2"])

    assert result.exit_code == 0
    assert "Item 1" in result.output
    assert "Item 2" in result.output
    assert "Item 3" not in result.output


def test_search_prints_results_with_scores(mock_manager: MagicMock) -> None:
    mock_manager.search_items.return_value = [
        ScoredKnowledgeItem(make_item(1, "Async in Python"), 6.70),
        ScoredKnowledgeItem(make_item(2, "Notes"), 0.69),
    ]

    result = runner.invoke(app, ["search", "python async"])

    assert result.exit_code == 0
    assert "Async in Python" in result.output
    assert "Notes" in result.output
    assert "6.70" in result.output
    assert "0.69" in result.output
    assert result.output.index("Async in Python") < result.output.index("Notes")
    mock_manager.search_items.assert_called_once_with("python async", 10)


def test_search_prints_cyrillic_titles(mock_manager: MagicMock) -> None:
    mock_manager.search_items.return_value = [ScoredKnowledgeItem(make_item(1, "Питон"), 3.5)]

    result = runner.invoke(app, ["search", "питон"])

    assert result.exit_code == 0
    assert "Питон" in result.output


def test_search_no_match(mock_manager: MagicMock) -> None:
    mock_manager.search_items.return_value = []

    result = runner.invoke(app, ["search", "NonexistentQuery"])

    assert result.exit_code == 0
    assert "No knowledge items found matching 'NonexistentQuery'." in result.output


def test_search_with_empty_query(mock_manager: MagicMock) -> None:
    mock_manager.search_items.side_effect = InvalidInputError("Query cannot be empty.")

    result = runner.invoke(app, ["search", " "])

    assert result.exit_code == 2
    assert "Query cannot be empty." in result.output


def test_delete_prints_deleted_item(mock_manager: MagicMock) -> None:
    mock_manager.delete_item.return_value = make_item()

    result = runner.invoke(app, ["delete", "1"])

    assert result.exit_code == 0
    assert "Deleted item: Title (ID: 1)" in result.output
    mock_manager.delete_item.assert_called_once_with(1)


def test_delete_with_nonexistent_id(mock_manager: MagicMock) -> None:
    mock_manager.delete_item.side_effect = ItemNotFoundError(67)

    result = runner.invoke(app, ["delete", "67"])

    assert result.exit_code == 1
    assert "No item with ID 67." in result.output
