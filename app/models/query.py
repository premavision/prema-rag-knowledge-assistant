from typing import List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = Field(default=None, description="Override default retrieval depth")


class Citation(BaseModel):
    doc_id: str
    doc_title: str
    chunk_id: str
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    citations: List[Citation]
