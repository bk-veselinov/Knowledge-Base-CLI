from knowledge.errors import InvalidInputError
from knowledge.errors import ItemNotFoundError

from knowledge.models import KnowledgeItem
from knowledge.repository import SqliteRepository

TITLE_MAX_LENGTH = 250

class KnowledgeManager:
    """Manages the knowledge base."""

    def __init__(self, repository: SqliteRepository) -> None:
        self.repository = repository

    def add_item(self, title: str, content: str) -> KnowledgeItem:
        title = self._require_text("Title", title)
        content = self._require_text("Content", content)

        if len(title) > TITLE_MAX_LENGTH:
            raise InvalidInputError(f"Title cannot exceed {TITLE_MAX_LENGTH} characters.")
        
        return self.repository.add(title, content)

    def get_item(self, item_id: int) -> KnowledgeItem | None:
        item = self.repository.get(item_id)

        if item is None:
            raise ItemNotFoundError(item_id)
        
        return item

    def list_items(self) -> list[KnowledgeItem]:
        return self.repository.list_all()

    def delete_item(self, item_id: int) -> KnowledgeItem:
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