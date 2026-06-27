from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_ollama import OllamaEmbeddings

from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


def get_chroma_collection(collection_name: str = "vera_docs"):
    """Returns the ChromaDB collection."""
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


def retrieve(query: str, collection_name: str = "vera_docs") -> List[Dict[str, Any]]:
    """
    Semantic search: takes a natural language query, returns the top-K
    most relevant chunks from ChromaDB with their citation metadata.

    Args:
        query: The user's question.
        collection_name: ChromaDB collection to search.

    Returns:
        List of dicts, each with:
            - text:     the matched chunk content
            - source:   filename it came from
            - page:     page number
            - score:    cosine similarity score (lower = more similar)
            - chunk_id: unique identifier
    """
    log.info(f"Retrieving top-{settings.top_k_results} chunks for query: '{query}'")

    # Embed the query using the same model used during ingestion
    embedder = OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )
    query_embedding = embedder.embed_query(query)

    collection = get_chroma_collection(collection_name)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=settings.top_k_results,
        include=["documents", "metadatas", "distances"],
    )

    # Unpack ChromaDB response format
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    output = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        output.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", "?"),
            "score": round(dist, 4),
            "chunk_id": meta.get("chunk_id", "?"),
        })

    # Filter out low-relevance chunks — score above 0.7 means poor cosine match
    output = [r for r in output if r["score"] <= 0.7]

    if not output:
        log.info("No relevant chunks found — query likely outside document scope")
        return []

    log.info(f"Retrieved {len(output)} chunks. Top match: '{output[0]['source']}' p.{output[0]['page']} (score={output[0]['score']})")
    return output


if __name__ == "__main__":
    import sys
    import json

    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What is this document about?"
    results = retrieve(query)

    print(f"\n🔍 Query: {query}\n")
    for i, r in enumerate(results, 1):
        print(f"[{i}] Source: {r['source']} | Page: {r['page']} | Score: {r['score']}")
        print(f"    {r['text'][:200]}...")
        print()
