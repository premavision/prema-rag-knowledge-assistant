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
        by_id: Dict[str, Document] = {doc.id: doc for doc in existing}
        by_id[document.id] = document
        self.save_all(list(by_id.values()))

    def get(self, document_id: str) -> Optional[Document]:
        for doc in self.load_all():
            if doc.id == document_id:
                return doc
        return None
