from typing import List, Dict, Any


def build_citations(chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Builds clean citation strings from retrieved chunks.
    Deduplicates by source + page combination.

    Args:
        chunks: Retrieved chunks from query_handler.

    Returns:
        List of formatted citation strings e.g. ["[1] NSP1.pdf, Page 2"]
    """
    seen = set()
    citations = []

    for chunk in chunks:
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "?")
        key = f"{source}::p{page}"

        if key not in seen:
            seen.add(key)
            citations.append(f"{source}, Page {page}")

    return [f"[{i+1}] {c}" for i, c in enumerate(citations)]


def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Combines chunk texts into a single context string for the LLM prompt.
    Each chunk is labeled with its source and page for traceability.

    Args:
        chunks: Retrieved chunks from query_handler.

    Returns:
        Formatted multi-chunk context string.
    """
    parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "?")
        text = chunk.get("text", "").strip()
        parts.append(f"[Source {i}: {source}, Page {page}]\n{text}")

    return "\n\n---\n\n".join(parts)
