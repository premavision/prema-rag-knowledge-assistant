import asyncio
from typing import List, Sequence

from openai import OpenAI

from app.services.embeddings.base import EmbeddingClient


class OpenAIEmbeddingClient(EmbeddingClient):
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        return await asyncio.to_thread(self._embed, texts)

    async def embed_query(self, text: str) -> List[float]:
        embeddings = await self.embed_documents([text])
        return embeddings[0]

    def _embed(self, texts: Sequence[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [item.embedding for item in response.data]
