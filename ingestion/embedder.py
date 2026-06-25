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


def embed_and_store(chunks: List[Dict[str, Any]], collection_name: str = "vera_docs") -> int:
    """
    Generates embeddings for each chunk and stores them in ChromaDB.

    Args:
        chunks: Output from loader.load_and_chunk_pdf()
        collection_name: ChromaDB collection to store into.

    Returns:
        Number of chunks successfully stored.
    """
    if not chunks:
        log.warning("No chunks provided to embedder. Skipping.")
        return 0

    log.info(f"Initializing Ollama embeddings with model: {settings.ollama_model}")
    embedder = OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )

    client = get_chroma_client()
    collection = get_or_create_collection(client, collection_name)

    texts = [c["text"] for c in chunks]
    ids = [c["chunk_id"] for c in chunks]
    metadatas = [
        {
            "source": c["source"],
            "page": c["page"],
            "chunk_id": c["chunk_id"],
        }
        for c in chunks
    ]

    log.info(f"Generating embeddings for {len(texts)} chunks — this may take a moment...")

    # Generate embeddings in one batch
    embeddings = embedder.embed_documents(texts)

    log.info(f"Storing {len(embeddings)} embeddings in ChromaDB collection '{collection_name}'")

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    stored_count = collection.count()
    log.info(f"ChromaDB collection '{collection_name}' now contains {stored_count} total chunks.")

    return len(embeddings)
