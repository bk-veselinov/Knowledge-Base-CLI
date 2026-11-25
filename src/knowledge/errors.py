class KnowledgeError(Exception):
    """Base class for every error in the knowledge project."""


class InvalidInputError(KnowledgeError):
    """Invalid input from the user."""


class ItemNotFoundError(KnowledgeError):
    """No item exists with the requested ID."""

    def __init__(self, item_id: int) -> None:
        super().__init__(f"No item with ID {item_id}.")
        self.item_id = item_id


class StorageError(KnowledgeError):
    """The storage file cannot be opened, read or written."""