from abc import ABC, abstractmethod
from typing import List, Sequence


class EmbeddingClient(ABC):
    @abstractmethod
    async def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        ...

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        ...
