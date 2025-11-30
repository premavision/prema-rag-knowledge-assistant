from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Prema RAG Knowledge Assistant"
    environment: Literal["local", "dev", "prod"] = "local"

    data_raw_path: Path = Path("./data/raw")
    data_processed_path: Path = Path("./data/processed")
    chroma_persist_dir: Path = Path("./data/vectorstore")

    openai_api_key: Optional[str] = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    chunk_size: int = 800
    chunk_overlap: int = 150
    rag_top_k: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
