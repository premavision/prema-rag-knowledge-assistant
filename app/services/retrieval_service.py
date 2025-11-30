from typing import List

from app.config.settings import Settings
from app.models.document import Chunk
from app.services.embeddings.base import EmbeddingClient
from app.services.vectorstore.base import VectorStore


class RetrievalService:
    def __init__(
        self,
        settings: Settings,
        embedding_client: EmbeddingClient,
        vector_store: VectorStore,
    ):
        self.settings = settings
        self.embedding_client = embedding_client
        self.vector_store = vector_store

    async def retrieve(self, query: str, top_k: int | None = None) -> List[Chunk]:
        embedding = await self.embedding_client.embed_query(query)
        return await self.vector_store.similarity_search(
            embedding=embedding,
            top_k=top_k or self.settings.rag_top_k,
        )
