from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_document_store
from app.infra.document_store import JsonDocumentStore
from app.models.document import Document

router = APIRouter()


@router.get("/documents", response_model=list[Document])
async def list_documents(
    document_store: JsonDocumentStore = Depends(get_document_store),
) -> list[Document]:
    return document_store.load_all()


@router.get("/documents/{document_id}", response_model=Document)
async def get_document(
    document_id: str,
    document_store: JsonDocumentStore = Depends(get_document_store),
) -> Document:
    document = document_store.get(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Document {document_id} not found"
        )
    return document
