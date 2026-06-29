from typing import List, Dict, Any


def build_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Builds clean citation dicts from retrieved chunks including source, page, and text snippet.
    Deduplicates by source + page combination.
    """
    seen = set()
    citations = []

    for chunk in chunks:
        source = chunk.get("source", "Unknown")
        page = chunk.get("page", "?")
        text = chunk.get("text", "").strip()
        key = f"{source}::p{page}"

        if key not in seen:
            seen.add(key)
            citations.append({
                "source": source,
                "page": page,
                "snippet": text,
            })

    res = []
    for i, c in enumerate(citations):
        res.append({
            "label": f"[{i+1}] {c['source']}, Page {c['page']}",
            "source": c["source"],
            "page": c["page"],
            "snippet": c["snippet"],
        })
    return res


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
