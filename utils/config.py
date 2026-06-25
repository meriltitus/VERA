from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"              
    embedding_model: str = "nomic-embed-text"

    # ChromaDB
    chroma_persist_dir: str = "./data/vectorstore"

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Retrieval
    top_k_results: int = 5

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = Path(__file__).resolve().parents[1] / ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    Call get_settings() from any module — reads .env once, reuses forever.
    """
    return Settings()
