from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

SourceType = Literal["local"]


class Document(BaseModel):
    id: str
    source: SourceType
    path: str
    title: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = None


class DocumentContent(BaseModel):
    document: Document
    text: str


class Chunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    path: str
    title: str
    source: SourceType
    score: Optional[float] = Field(default=None, description="Populated during retrieval")
