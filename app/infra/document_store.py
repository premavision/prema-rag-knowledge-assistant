import json
from pathlib import Path
from typing import Dict, List, Optional

from app.models.document import Document


class JsonDocumentStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_all(self) -> List[Document]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text())
        return [Document(**item) for item in raw]

    def save_all(self, documents: List[Document]) -> None:
        serialized = [doc.model_dump() for doc in documents]
        self.path.write_text(json.dumps(serialized, default=str, indent=2))

    def upsert(self, document: Document) -> None:
        existing = self.load_all()
        # Deduplicate by path - remove all old documents with same path
        # Keep only documents with different paths
        filtered = [doc for doc in existing if doc.path != document.path]
        # Add the new/updated document
        filtered.append(document)
        self.save_all(filtered)

    def get(self, document_id: str) -> Optional[Document]:
        for doc in self.load_all():
            if doc.id == document_id:
                return doc
        return None
