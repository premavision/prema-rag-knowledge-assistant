from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.config.settings import Settings, get_settings
from app.infra.document_store import JsonDocumentStore
from app.services.embeddings.openai_client import OpenAIEmbeddingClient
from app.services.llm.openai_client import OpenAILLMClient
from app.services.vectorstore.chroma_store import ChromaVectorStore


def get_document_store(settings: Settings = Depends(get_settings)) -> JsonDocumentStore:
    return JsonDocumentStore(settings.data_processed_path / "documents.json")


@lru_cache
def _embedding_client(settings: Settings) -> OpenAIEmbeddingClient:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured",
        )
    return OpenAIEmbeddingClient(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        base_url=settings.openai_base_url,
    )


def get_embedding_client(settings: Settings = Depends(get_settings)) -> OpenAIEmbeddingClient:
    return _embedding_client(settings)


@lru_cache
def _llm_client(settings: Settings) -> OpenAILLMClient:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured",
        )
    return OpenAILLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
    )


def get_llm_client(settings: Settings = Depends(get_settings)) -> OpenAILLMClient:
    return _llm_client(settings)


@lru_cache
def _vector_store(settings: Settings) -> ChromaVectorStore:
    persist_dir = settings.chroma_persist_dir
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    return ChromaVectorStore(persist_directory=persist_dir)


def get_vector_store(settings: Settings = Depends(get_settings)) -> ChromaVectorStore:
    return _vector_store(settings)
