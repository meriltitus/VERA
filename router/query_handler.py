from typing import List, Dict, Any

from router.classifier import classify_query, QueryType
from vectorstore.retriever import retrieve
from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


# How many chunks to retrieve per query type
TOP_K_BY_TYPE = {
    QueryType.FACTUAL: 3,     # Precise — fewer, higher relevance
    QueryType.CONCEPTUAL: 5,  # Balanced — default
    QueryType.SUMMARY: 8,     # Broad — needs more context
}


def handle_query(query: str, collection_name: str = "vera_docs") -> Dict[str, Any]:
    """
    Full router pipeline: classify → retrieve with appropriate strategy.

    Args:
        query: The user's natural language question.
        collection_name: ChromaDB collection to search.

    Returns:
        Dict with:
            - query:       original query
            - query_type:  classified type
            - chunks:      retrieved evidence chunks
            - top_k:       how many chunks were fetched
    """
    log.info(f"Router received query: '{query}'")

    # Step 1: Classify
    query_type = classify_query(query)

    # Step 2: Determine retrieval depth
    top_k = TOP_K_BY_TYPE[query_type]
    log.info(f"Query type: {query_type.value} → fetching top {top_k} chunks")

    # Step 3: Override top_k temporarily for this retrieval
    original_top_k = settings.top_k_results
    settings.__dict__["top_k_results"] = top_k  # temporary override

    chunks = retrieve(query, collection_name=collection_name)

    # Restore original setting
    settings.__dict__["top_k_results"] = original_top_k

    # Trim to correct top_k in case retriever returned default
    chunks = chunks[:top_k]

    log.info(f"Router returning {len(chunks)} chunks for aggregation")

    return {
        "query": query,
        "query_type": query_type.value,
        "chunks": chunks,
        "top_k": top_k,
    }
