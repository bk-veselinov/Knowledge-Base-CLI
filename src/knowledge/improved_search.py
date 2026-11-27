import math
import re

from knowledge.errors import InvalidInputError
from knowledge.models import KnowledgeItem, ScoredKnowledgeItem

TITLE_WEIGHT = 3.5
CONTENT_WEIGHT = 1.0
PHRASE_TITLE_BONUS = 4
PHRASE_CONTENT_BONUS = 2

EXCLUDED_TERMS = {"the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of", "for", "with", "by", "from",
                   "и", "в", "на", "но", "с", "по", "за", "из", "от", "до", "при"}

def _tokenize(text: str) -> list[str]:
    """Tokenize the input text into a list of terms."""
    return [term for term in re.findall(r'\w+', text.casefold())
                if term not in EXCLUDED_TERMS]

def _to_scored_knowledge_items(score: float, knowledge_items: KnowledgeItem) -> ScoredKnowledgeItem:
    """Create a ScoredKnowledgeItem from a KnowledgeItem and its score."""
    return ScoredKnowledgeItem(knowledge_item=knowledge_items, score=score)

def _frequency_count(terms: list[str]) -> dict[str, int]:
    """Count the frequency of each term in the list."""
    freq_count = {}
    for term in terms:
        if term in freq_count:
            freq_count[term] += 1
        else:
            freq_count[term] = 1
    return freq_count

def _score_knowledge_item(query_terms: list[str], knowledge_item: KnowledgeItem) -> float:
    """Score knowledge items based on their relevance to the query."""
    title_terms = _tokenize(knowledge_item.title.strip())
    content_terms = _tokenize(knowledge_item.content.strip())
    content_freq = _frequency_count(content_terms)

    score = 0.0
    query_terms_matched = 0
    for term in query_terms:
        score_increase = 0
        if term in title_terms:
            score_increase += TITLE_WEIGHT

        score_increase += CONTENT_WEIGHT * math.log(1 + content_freq.get(term, 0))
        score += score_increase
        if score_increase > 0:
            query_terms_matched += 1

    score *= (query_terms_matched / len(query_terms)) ** 2

    if len(set(query_terms)) == 1:
        return score
    
    clean_query = " ".join(query_terms)
    if clean_query in " ".join(title_terms):
        score += PHRASE_TITLE_BONUS
    if clean_query in " ".join(content_terms):
        score += PHRASE_CONTENT_BONUS

    return score

def search_knowledge_items(query: str, knowledge_items: list[KnowledgeItem], limit: int = 10) -> list[ScoredKnowledgeItem]:
    """Search for knowledge items based on a query."""
    if limit <= 0:
        raise InvalidInputError("Limit must be a positive integer.")
    
    clean_query = query.strip().casefold()
    if not clean_query:
        raise InvalidInputError("Query cannot be empty.")

    query_terms = _tokenize(clean_query)
    if not query_terms:
        raise InvalidInputError("Query must contain valid terms not common words.")

    scored_items = []
    for item in knowledge_items:
        score = _score_knowledge_item(query_terms, item)

        if score > 0:
            scored_items.append((score, item))
    
    sorted_items = sorted(scored_items, key=lambda x: x[0], reverse=True)
    return [_to_scored_knowledge_items(score, item) for score, item in sorted_items[:limit]]
