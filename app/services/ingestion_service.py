from typing import List
from uuid import uuid4

from app.config.settings import Settings
from app.infra.document_store import JsonDocumentStore
from app.models.document import Chunk, Document, DocumentContent
from app.models.ingest import IngestResponse, IngestResult
from app.services.chunker import chunk_text
from app.services.embeddings.base import EmbeddingClient
from app.services.sources.base import DocumentSource
from app.services.vectorstore.base import VectorStore


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        embedding_client: EmbeddingClient,
        vector_store: VectorStore,
        document_store: JsonDocumentStore,
    ):
        self.settings = settings
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.document_store = document_store

    async def ingest(self, source: DocumentSource) -> IngestResponse:
        results: List[IngestResult] = []
        total_chunks = 0
        errors: List[str] = []

        for item in source.load():
            result = await self._process_document(item)
            results.append(result)
            if result.error:
                errors.append(result.error)
            total_chunks += result.chunks

        return IngestResponse(
            results=results,
            total_documents=len(results),
            total_chunks=total_chunks,
            errors=errors,
        )

    async def _process_document(self, content: DocumentContent) -> IngestResult:
        try:
            chunks = self._build_chunks(content)
            if not chunks:
                return IngestResult(document=content.document, chunks=0, error="No text extracted")

            embeddings = await self.embedding_client.embed_documents([c.content for c in chunks])
            await self.vector_store.add(chunks, embeddings)
            self.document_store.upsert(content.document)
            return IngestResult(document=content.document, chunks=len(chunks))
        except Exception as exc:  # noqa: BLE001
            return IngestResult(document=content.document, chunks=0, error=str(exc))

    def _build_chunks(self, content: DocumentContent) -> List[Chunk]:
        text_chunks = chunk_text(
            content.text,
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
        )
        return [
            Chunk(
                id=str(uuid4()),
                document_id=content.document.id,
                content=chunk_text_piece,
                chunk_index=index,
                path=content.document.path,
                title=content.document.title,
                source=content.document.source,
            )
            for index, chunk_text_piece in enumerate(text_chunks)
        ]
