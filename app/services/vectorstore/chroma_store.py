import asyncio
import os
from collections import OrderedDict
from pathlib import Path
from typing import List, Sequence, Tuple

# Set default ChromaDB environment variables (must be strings, not None)
os.environ["CHROMA_SERVER_HOST"] = os.environ.get("CHROMA_SERVER_HOST", "")
os.environ["CHROMA_SERVER_HTTP_PORT"] = os.environ.get("CHROMA_SERVER_HTTP_PORT", "")
os.environ["CHROMA_SERVER_GRPC_PORT"] = os.environ.get("CHROMA_SERVER_GRPC_PORT", "")
os.environ["CLICKHOUSE_HOST"] = os.environ.get("CLICKHOUSE_HOST", "")
os.environ["CLICKHOUSE_PORT"] = os.environ.get("CLICKHOUSE_PORT", "")

# Hide .env before importing chromadb to prevent it from reading app env vars
_env_file_path = Path(".env")
_env_backup_path = None

if _env_file_path.exists():
    _env_backup_path = _env_file_path.with_suffix(".env.tmp")
    if _env_backup_path.exists():
        _env_backup_path.unlink()
    _env_file_path.rename(_env_backup_path)

try:
    # Import chromadb (Settings won't read .env since it's hidden)
    import chromadb
finally:
    # Restore .env file immediately after import
    if _env_backup_path and _env_backup_path.exists():
        if _env_file_path.exists():
            _env_file_path.unlink()
        _env_backup_path.rename(_env_file_path)
        # Clear settings cache so it re-reads .env
        from app.config.settings import get_settings
        get_settings.cache_clear()

# Helper functions to temporarily hide .env when creating ChromaDB Settings
_env_file_path = Path(".env")

def _hide_env_file():
    """Temporarily rename .env file to prevent ChromaDB Settings from reading it."""
    backup_path = _env_file_path.with_suffix(".env.tmp")
    if _env_file_path.exists():
        if backup_path.exists():
            backup_path.unlink()
        _env_file_path.rename(backup_path)
        return backup_path
    return None

def _restore_env_file(backup_path):
    """Restore .env file after creating ChromaDB Settings."""
    if backup_path and backup_path.exists():
        if _env_file_path.exists():
            _env_file_path.unlink()
        backup_path.rename(_env_file_path)

from app.models.document import Chunk
from app.services.vectorstore.base import VectorStore


class ChromaVectorStore(VectorStore):
    def __init__(self, persist_directory: Path, collection_name: str = "documents"):
        self.persist_directory = persist_directory
        # Hide .env file before creating Settings to prevent reading app env vars
        backup_path = _hide_env_file()
        try:
            # Create Settings with persist_directory and ensure persistence
            settings = chromadb.config.Settings(
                persist_directory=str(persist_directory),
                chroma_db_impl='duckdb+parquet'  # Use parquet for persistence
            )
            self.client = chromadb.Client(settings=settings)
            # Create collection without embedding_function to use our own embeddings
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None  # Use our own embeddings, not ChromaDB's default
            )
            # Fix: Ensure collection has _client attribute (bug in ChromaDB 0.3.23)
            if not hasattr(self.collection, '_client') or getattr(self.collection, '_client', None) is None:
                self.collection._client = self.client
        finally:
            # Restore .env file
            _restore_env_file(backup_path)

    async def add(
        self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]
    ) -> None:
        await asyncio.to_thread(self._add_sync, chunks, embeddings)

    def _add_sync(
        self, chunks: Sequence[Chunk], embeddings: Sequence[Sequence[float]]
    ) -> None:
        # Ensure collection has _client before adding
        if not hasattr(self.collection, '_client') or getattr(self.collection, '_client', None) is None:
            self.collection._client = self.client
        
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
        # Ensure collection has _client (fix for ChromaDB 0.3.23 bug)
        # Must set _client before any collection operations
        if not hasattr(self.collection, '_client') or getattr(self.collection, '_client', None) is None:
            self.collection._client = self.client
        
        # Check if collection is empty (also needs _client)
        try:
            count = self.collection.count()
        except AttributeError:
            # If count fails, try setting _client again
            self.collection._client = self.client
            count = self.collection.count()
        
        if count == 0:
            return []
        
        # Don't request more results than available
        n_results = min(top_k, count)
        
        result = self.collection.query(
            query_embeddings=[list(embedding)],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        chunks: List[Chunk] = []
        
        # Handle empty results
        if not result.get("metadatas") or not result["metadatas"][0]:
            return chunks
        
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

    async def delete_by_path(self, path: str) -> None:
        """Delete all chunks for documents with the given path."""
        return await asyncio.to_thread(self._delete_by_path_sync, path)

    def _delete_by_path_sync(self, path: str) -> None:
        """Delete all chunks for documents with the given path (synchronous)."""
        # Ensure collection has _client
        if not hasattr(self.collection, '_client') or getattr(self.collection, '_client', None) is None:
            self.collection._client = self.client
        
        # Get all chunks with this path
        try:
            all_data = self.collection.get(
                where={"path": path},
                include=["metadatas"],
                limit=10000
            )
            # IDs are always returned, even if not in include
            if all_data.get("ids"):
                # Delete chunks by IDs
                self.collection.delete(ids=all_data["ids"])
        except Exception:
            # If deletion fails, continue - it's not critical
            pass

    def list_documents(self) -> List[Tuple[str, str]]:
        # Collect unique document ids from stored metadata.
        # Ensure collection has _client
        if not hasattr(self.collection, '_client') or getattr(self.collection, '_client', None) is None:
            self.collection._client = self.client
        
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
