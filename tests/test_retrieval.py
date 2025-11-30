from typing import List, Sequence

import pytest

from app.config.settings import Settings
from app.models.document import Chunk
from app.services.embeddings.base import EmbeddingClient
from app.services.retrieval_service import RetrievalService
from app.services.vectorstore.base import VectorStore


class _FakeEmbeddingClient(EmbeddingClient):
    async def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return [[float(len(text))] for text in texts]

    async def embed_query(self, text: str) -> List[float]:
        return [float(len(text))]


class _FakeVectorStore(VectorStore):
    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks

    async def add(self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]) -> None:
        raise NotImplementedError

    async def similarity_search(self, embedding: Sequence[float], top_k: int) -> List[Chunk]:
        # Return top_k slices ignoring embedding for test purposes.
        return self.chunks[:top_k]

    def list_documents(self):
        return []


@pytest.mark.asyncio
async def test_retrieval_returns_requested_top_k():
    chunks = [
        Chunk(
            id="1",
            document_id="doc",
            content="alpha",
            chunk_index=0,
            path="/tmp/a.txt",
            title="a",
            source="local",
        ),
        Chunk(
            id="2",
            document_id="doc",
            content="beta",
            chunk_index=1,
            path="/tmp/a.txt",
            title="a",
            source="local",
        ),
    ]
    service = RetrievalService(
        settings=Settings(),
        embedding_client=_FakeEmbeddingClient(),
        vector_store=_FakeVectorStore(chunks),
    )
    result = await service.retrieve("hello", top_k=1)
    assert len(result) == 1
    assert result[0].id == "1"
