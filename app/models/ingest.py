from typing import List, Optional

from pydantic import BaseModel

from app.models.document import Document, SourceType


class IngestRequest(BaseModel):
    source_type: SourceType = "local"
    path: Optional[str] = None
    tags: Optional[List[str]] = None


class IngestResult(BaseModel):
    document: Document
    chunks: int
    error: Optional[str] = None


class IngestResponse(BaseModel):
    results: List[IngestResult]
    total_documents: int
    total_chunks: int
    errors: List[str]
