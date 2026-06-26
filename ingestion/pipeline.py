from utils.logger import get_logger
from ingestion.loader import load_and_chunk_pdf
from ingestion.embedder import embed_and_store

log = get_logger(__name__)


def run_ingestion(pdf_path: str, collection_name: str = "vera_docs", real_filename: str = None) -> dict:
    """
    Full ingestion pipeline: PDF → chunks → embeddings → ChromaDB.

    Args:
        pdf_path: Path to the PDF file (may be a temp path).
        collection_name: ChromaDB collection to store into.
        real_filename: Original filename to use in citations (overrides temp path name).

    Returns:
        Summary dict with source, chunks_created, chunks_stored.
    """
    display_name = real_filename or pdf_path
    log.info(f"=== VERA Ingestion Pipeline START: {display_name} ===")

    # Stage 1: Load and chunk — pass real filename for citation metadata
    chunks = load_and_chunk_pdf(pdf_path, real_filename=real_filename)

    # Stage 2: Embed and store
    stored = embed_and_store(chunks, collection_name=collection_name)

    summary = {
        "source": display_name,
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
