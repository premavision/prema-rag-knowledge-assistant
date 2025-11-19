from abc import ABC, abstractmethod
from typing import Iterable, List, Sequence, Tuple

from app.models.document import Chunk


class VectorStore(ABC):
    @abstractmethod
    async def add(
        self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]
    ) -> None:
        ...

    @abstractmethod
    async def similarity_search(
        self, embedding: Sequence[float], top_k: int
    ) -> List[Chunk]:
        ...

    @abstractmethod
    def list_documents(self) -> List[Tuple[str, str]]:
        """Return list of (document_id, title) present in the store."""
        ...
