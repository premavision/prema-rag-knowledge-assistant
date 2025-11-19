import asyncio
from collections import OrderedDict
from pathlib import Path
from typing import List, Sequence, Tuple

import chromadb

from app.models.document import Chunk
from app.services.vectorstore.base import VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_directory: Path, collection_name: str = "documents"):
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.collection = self.client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    async def add(
        self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]
    ) -> None:
        await asyncio.to_thread(self._add_sync, chunks, embeddings)

    def _add_sync(
        self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]
    ) -> None:
        ids = [chunk.id for chunk in chunks]
        documents = [chunk.content for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk.document_id,
                "title": chunk.title,
                "path": chunk.path,
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]
        self.collection.add(ids=ids, embeddings=list(embeddings), documents=documents, metadatas=metadatas)

    async def similarity_search(self, embedding: Sequence[float], top_k: int) -> List[Chunk]:
        return await asyncio.to_thread(self._similarity_search_sync, embedding, top_k)

    def _similarity_search_sync(self, embedding: Sequence[float], top_k: int) -> List[Chunk]:
        result = self.collection.query(
            query_embeddings=[list(embedding)],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        chunks: List[Chunk] = []
        for idx, metadata in enumerate(result.get("metadatas", [])[0]):
            chunk = Chunk(
                id=result["ids"][0][idx],
                document_id=metadata["document_id"],
                content=result["documents"][0][idx],
                chunk_index=metadata["chunk_index"],
                path=metadata["path"],
                title=metadata["title"],
                source=metadata["source"],
                score=float(result.get("distances", [[0]])[0][idx]),
            )
            chunks.append(chunk)
        return chunks

    def list_documents(self) -> List[Tuple[str, str]]:
        # Collect unique document ids from stored metadata.
        data = self.collection.get(include=["metadatas"], limit=10000)
        seen: OrderedDict[str, str] = OrderedDict()
        for metadata in data.get("metadatas", []):
            if not metadata:
                continue
            doc_id = metadata.get("document_id")
            title = metadata.get("title", "")
            if doc_id and doc_id not in seen:
                seen[doc_id] = title
        return list(seen.items())
