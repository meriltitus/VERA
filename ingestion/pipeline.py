from utils.logger import get_logger
from ingestion.loader import load_and_chunk_pdf
from ingestion.embedder import embed_and_store

log = get_logger(__name__)


def run_ingestion(pdf_path: str, collection_name: str = "vera_docs") -> dict:
    """
    Full ingestion pipeline: PDF → chunks → embeddings → ChromaDB.

    Args:
        pdf_path: Path to the PDF file.
        collection_name: ChromaDB collection to store into.

    Returns:
        Summary dict with source, chunks_created, chunks_stored.
    """
    log.info(f"=== VERA Ingestion Pipeline START: {pdf_path} ===")

    # Stage 1: Load and chunk
    chunks = load_and_chunk_pdf(pdf_path)

    # Stage 2: Embed and store
    stored = embed_and_store(chunks, collection_name=collection_name)

    summary = {
        "source": pdf_path,
        "chunks_created": len(chunks),
        "chunks_stored": stored,
        "collection": collection_name,
        "status": "success",
    }

    log.info(f"=== VERA Ingestion Pipeline COMPLETE: {summary} ===")
    return summary


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m ingestion.pipeline <path_to_pdf>")
        sys.exit(1)

    result = run_ingestion(sys.argv[1])
    print(f"\n✅ Ingestion complete: {result}")
