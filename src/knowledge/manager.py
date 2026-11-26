from knowledge.errors import InvalidInputError
from knowledge.errors import ItemNotFoundError

from knowledge.models import KnowledgeItem
from knowledge.repository import SqliteRepository
from knowledge.improved_search import search_knowledge_items

TITLE_MAX_LENGTH = 250

class KnowledgeManager:
    """Manages the knowledge base."""

    def __init__(self, repository: SqliteRepository) -> None:
        self.repository = repository

    def add_item(self, title: str, content: str) -> KnowledgeItem:
        """Add a new knowledge item."""
        title = self._require_text("Title", title)
        content = self._require_text("Content", content)

        if len(title) > TITLE_MAX_LENGTH:
            raise InvalidInputError(f"Title cannot exceed {TITLE_MAX_LENGTH} characters.")
        
        return self.repository.add(title, content)

    def get_item(self, item_id: int) -> KnowledgeItem:
        """Get a knowledge item by ID."""
        item_id = self._require_valid_id(item_id)
        item = self.repository.get(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)
        
        return item

    def list_items(self) -> list[KnowledgeItem]:
        """List all knowledge items."""
        return self.repository.list_all()

    def search_items(self, query: str, limit: int = 10) -> list[KnowledgeItem]:
        """Search for knowledge items based on a query."""
        query = self._require_text("Query", query)
        items = self.repository.list_all()
        return search_knowledge_items(query, items, limit)

    def delete_item(self, item_id: int) -> KnowledgeItem:
        """Delete a knowledge item by ID."""
        item_id = self._require_valid_id(item_id)
        item = self.repository.get(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)
        
        self.repository.delete(item_id)
        return item

    @staticmethod
    def _require_text(field_name: str, value: str) -> str:
        value = value.strip()

        if not value:
            raise InvalidInputError(f"{field_name} cannot be empty.")
        
        return value

    @staticmethod
    def _require_valid_id(item_id: int) -> int:
        if item_id <= 0:
            raise InvalidInputError("Item ID must be a positive integer.")
        
        return item_id