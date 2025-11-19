from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import (
    get_document_store,
    get_embedding_client,
    get_settings,
    get_vector_store,
)
from app.infra.document_store import JsonDocumentStore
from app.models.ingest import IngestRequest, IngestResponse
from app.services.embeddings.base import EmbeddingClient
from app.services.ingestion_service import IngestionService
from app.services.sources.local_folder import LocalFolderSource
from app.services.vectorstore.base import VectorStore
from app.config.settings import Settings


router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    body: IngestRequest,
    settings: Settings = Depends(get_settings),
    embedding_client: EmbeddingClient = Depends(get_embedding_client),
    vector_store: VectorStore = Depends(get_vector_store),
    document_store: JsonDocumentStore = Depends(get_document_store),
) -> IngestResponse:
    target_path = Path(body.path or settings.data_raw_path)
    if not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Path does not exist: {target_path}",
        )

    source = LocalFolderSource(folder=target_path, tags=body.tags)
    service = IngestionService(
        settings=settings,
        embedding_client=embedding_client,
        vector_store=vector_store,
        document_store=document_store,
    )
    return await service.ingest(source)
