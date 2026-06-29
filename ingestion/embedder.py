from typing import List, Dict, Any

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_ollama import OllamaEmbeddings

from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


def get_chroma_client() -> chromadb.PersistentClient:
    """Returns a persistent ChromaDB client pointed at the configured directory."""
    return chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_or_create_collection(client: chromadb.PersistentClient, collection_name: str = "vera_docs"):
    """Gets or creates the main VERA document collection."""
    return client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )


import hashlib


def embed_and_store(chunks: List[Dict[str, Any]], collection_name: str = "vera_docs") -> int:
    """
    Generates embeddings for each chunk and stores them in ChromaDB with Zero-Duplication hashing.

    Args:
        chunks: Output from loader.load_and_chunk_pdf()
        collection_name: ChromaDB collection to store into.

    Returns:
        Number of chunks successfully stored.
    """
    if not chunks:
        log.warning("No chunks provided to embedder. Skipping.")
        return 0

    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)

    # Stage 1: Deduplicate chunks by content hash
    existing_ids = set(collection.get()["ids"]) if collection.count() > 0 else set()
    to_embed = []
    seen_hashes = set()

    for c in chunks:
        content_hash = hashlib.md5(c["text"].encode('utf-8')).hexdigest()[:16]
        chunk_id = f"chunk_{content_hash}"
        if content_hash not in seen_hashes and chunk_id not in existing_ids:
            seen_hashes.add(content_hash)
            c_copy = dict(c)
            c_copy["chunk_id"] = chunk_id
            to_embed.append(c_copy)

    if not to_embed:
        log.info("Zero-Duplication Engine: All provided chunks already exist in vector storage. Skipping embedding.")
        return 0

    log.info(f"Zero-Duplication Engine: {len(to_embed)} new unique chunks to embed (skipped duplicates).")
    log.info(f"Initializing Ollama embeddings with model: {settings.ollama_embed_model}")
    embedder = OllamaEmbeddings(
        model=settings.ollama_embed_model,
        base_url=settings.ollama_base_url,
    )

    texts = [c["text"] for c in to_embed]
    ids = [c["chunk_id"] for c in to_embed]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"],
            "chunk_id": c["chunk_id"],
        }
        for c in to_embed
    ]

    log.info(f"Generating embeddings for {len(texts)} new chunks...")
    embeddings = embedder.embed_documents(texts)

    log.info(f"Storing {len(embeddings)} new embeddings in ChromaDB collection '{collection_name}'")

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    stored_count = collection.count()
    log.info(f"ChromaDB collection '{collection_name}' now contains {stored_count} total unique chunks.")

    return len(embeddings)
