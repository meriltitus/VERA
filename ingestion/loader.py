from pathlib import Path
from typing import List, Dict, Any

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from utils.config import get_settings
from utils.logger import get_logger

log = get_logger(__name__)
settings = get_settings()


def load_and_chunk_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Loads a PDF and splits it into chunks with citation metadata.

    Args:
        pdf_path: Absolute or relative path to the PDF file.

    Returns:
        List of dicts, each with:
            - text: the chunk content
            - source: filename
            - page: page number (1-indexed)
            - chunk_id: unique identifier
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    log.info(f"Loading PDF: {path.name}")

    loader = PyPDFLoader(str(path))
    raw_pages = loader.load()
    log.info(f"Loaded {len(raw_pages)} pages from {path.name}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks = splitter.split_documents(raw_pages)
    log.info(f"Split into {len(chunks)} chunks (size={settings.chunk_size}, overlap={settings.chunk_overlap})")

    results = []
    for i, chunk in enumerate(chunks):
        results.append({
            "text": chunk.page_content.strip(),
            "source": path.name,
            "page": chunk.metadata.get("page", 0) + 1,  # 1-indexed
            "chunk_id": f"{path.stem}_chunk_{i:04d}",
        })

    # Filter out empty chunks
    results = [r for r in results if len(r["text"]) > 20]
    log.info(f"Final chunk count after filtering: {len(results)}")

    return results
