from pathlib import Path
from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.config.settings import Settings, get_settings
from app.infra.document_store import JsonDocumentStore
from app.services.embeddings.openai_client import OpenAIEmbeddingClient
from app.services.llm.openai_client import OpenAILLMClient
from app.services.vectorstore.chroma_store import ChromaVectorStore

# Module-level cache for clients
_embedding_client_cache: OpenAIEmbeddingClient | None = None
_llm_client_cache: OpenAILLMClient | None = None
_vector_store_cache: ChromaVectorStore | None = None
_cached_settings: Settings | None = None


def get_document_store(settings: Settings = Depends(get_settings)) -> JsonDocumentStore:
    return JsonDocumentStore(settings.data_processed_path / "documents.json")


def get_embedding_client(settings: Settings = Depends(get_settings)) -> OpenAIEmbeddingClient:
    global _embedding_client_cache, _cached_settings
    
    # Return cached client if settings haven't changed
    if _embedding_client_cache is not None and _cached_settings is settings:
        return _embedding_client_cache
    
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured",
        )
    
    _embedding_client_cache = OpenAIEmbeddingClient(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        base_url=settings.openai_base_url,
    )
    _cached_settings = settings
    return _embedding_client_cache


def get_llm_client(settings: Settings = Depends(get_settings)) -> OpenAILLMClient:
    global _llm_client_cache, _cached_settings
    
    # Return cached client if settings haven't changed
    if _llm_client_cache is not None and _cached_settings is settings:
        return _llm_client_cache
    
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OPENAI_API_KEY not configured",
        )
    
    _llm_client_cache = OpenAILLMClient(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        base_url=settings.openai_base_url,
    )
    _cached_settings = settings
    return _llm_client_cache


def get_vector_store(settings: Settings = Depends(get_settings)) -> ChromaVectorStore:
    global _vector_store_cache, _cached_settings
    
    # Return cached store if settings haven't changed
    if _vector_store_cache is not None and _cached_settings is settings:
        return _vector_store_cache
    
    persist_dir = settings.chroma_persist_dir
    Path(persist_dir).mkdir(parents=True, exist_ok=True)
    _vector_store_cache = ChromaVectorStore(persist_directory=persist_dir)
    _cached_settings = settings
    return _vector_store_cache
