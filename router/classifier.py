from enum import Enum
from utils.logger import get_logger

log = get_logger(__name__)


class QueryType(str, Enum):
    FACTUAL = "factual"        # "What is Kerberos?" — specific fact lookup
    CONCEPTUAL = "conceptual"  # "How does mutual authentication work?" — explanation
    SUMMARY = "summary"        # "Summarize this document" — broad overview


# Keyword signals for each query type
FACTUAL_SIGNALS = [
    "what is", "what are", "who is", "when did", "where is",
    "define", "definition", "name the", "list the", "which",
]

SUMMARY_SIGNALS = [
    "summarize", "summary", "overview", "briefly explain",
    "give me a summary", "what is this document about",
    "what does this cover", "outline",
]


def classify_query(query: str) -> QueryType:
    """
    Classifies a natural language query into one of three types.
    Uses keyword matching — fast, local, no LLM call needed.

    Args:
        query: The user's question.

    Returns:
        QueryType enum value.
    """
    q = query.lower().strip()

    # Check summary signals first (most specific)
    for signal in SUMMARY_SIGNALS:
        if signal in q:
            log.info(f"Query classified as SUMMARY (matched: '{signal}')")
            return QueryType.SUMMARY

    # Check factual signals
    for signal in FACTUAL_SIGNALS:
        if q.startswith(signal) or f" {signal}" in q:
            log.info(f"Query classified as FACTUAL (matched: '{signal}')")
            return QueryType.FACTUAL

    # Default: conceptual (open-ended explanation)
    log.info("Query classified as CONCEPTUAL (default)")
    return QueryType.CONCEPTUAL
