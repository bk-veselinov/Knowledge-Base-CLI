from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class KnowledgeItem:
    """One stored piece of knowledge."""

    id: int
    title: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class ScoredKnowledgeItem:
    """A knowledge item with a search score."""

    knowledge_item: KnowledgeItem
    score: float
