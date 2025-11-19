import pytest

from app.config.settings import Settings
from app.models.document import Chunk
from app.services.llm.base import LLMClient
from app.services.rag_service import RagService
from app.services.retrieval_service import RetrievalService


class _FakeRetrievalService(RetrievalService):
    def __init__(self, chunks):
        self._chunks = chunks

    async def retrieve(self, query: str, top_k: int | None = None):
        return self._chunks


class _FakeLLM(LLMClient):
    async def generate(self, prompt: str) -> str:
        assert "[1]" in prompt  # ensure citations markers included
        assert "Context" in prompt
        return "Test answer with [1]"


@pytest.mark.asyncio
async def test_prompt_includes_citations_and_returns_response():
    chunk = Chunk(
        id="chunk-1",
        document_id="doc-1",
        content="Important content goes here.",
        chunk_index=0,
        path="/tmp/doc.txt",
        title="Doc",
        source="local",
    )
    rag = RagService(
        settings=Settings(),
        retrieval_service=_FakeRetrievalService([chunk]),
        llm_client=_FakeLLM(),
    )
    response = await rag.query(question="What is this?", top_k=1)
    assert "Test answer" in response.answer
    assert len(response.citations) == 1
    assert response.citations[0].chunk_id == "chunk-1"
