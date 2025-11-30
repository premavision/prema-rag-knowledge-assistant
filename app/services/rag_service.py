from typing import List

from app.config.settings import Settings
from app.models.document import Chunk
from app.models.query import Citation, QueryResponse
from app.services.llm.base import LLMClient
from app.services.retrieval_service import RetrievalService


class RagService:
    def __init__(
        self,
        settings: Settings,
        retrieval_service: RetrievalService,
        llm_client: LLMClient,
    ):
        self.settings = settings
        self.retrieval_service = retrieval_service
        self.llm_client = llm_client

    async def query(self, question: str, top_k: int | None = None) -> QueryResponse:
        chunks = await self.retrieval_service.retrieve(question, top_k)
        prompt = self._build_prompt(question, chunks)
        answer = await self.llm_client.generate(prompt)
        citations = self._build_citations(chunks)
        return QueryResponse(answer=answer, citations=citations)

    def _build_prompt(self, question: str, chunks: List[Chunk]) -> str:
        context_blocks = []
        for idx, chunk in enumerate(chunks, start=1):
            context_blocks.append(
                f"[{idx}] (Title: {chunk.title} | Path: {chunk.path})\n{chunk.content}"
            )
        context = "\n\n".join(context_blocks) if context_blocks else "No relevant context found."

        return (
            "You are a concise RAG assistant for Prema Vision.\n"
            "Use only the provided context to answer the question. "
            "If the answer is not in the context, say you do not have enough information. "
            "Always cite sources with [n] markers matching the context blocks.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )

    def _build_citations(self, chunks: List[Chunk]) -> List[Citation]:
        citations: List[Citation] = []
        for idx, chunk in enumerate(chunks, start=1):
            score = chunk.score if chunk.score is not None else 0.0
            citations.append(
                Citation(
                    doc_id=chunk.document_id,
                    doc_title=chunk.title,
                    chunk_id=chunk.id,
                    snippet=chunk.content[:280] + ("..." if len(chunk.content) > 280 else ""),
                    score=score,
                )
            )
        return citations
