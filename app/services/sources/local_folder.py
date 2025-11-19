from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from uuid import uuid4

from app.models.document import Document, DocumentContent
from app.services.parsers.markdown_parser import parse_markdown
from app.services.parsers.pdf_parser import parse_pdf
from app.services.parsers.text_parser import parse_text
from app.services.sources.base import DocumentSource


class LocalFolderSource(DocumentSource):
    SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

    def __init__(self, folder: Path, tags: Optional[List[str]] = None):
        self.folder = folder
        self.tags = tags or []
        self._parsers: Dict[str, callable] = {
            ".pdf": parse_pdf,
            ".md": parse_markdown,
            ".txt": parse_text,
        }

    def load(self) -> Iterable[DocumentContent]:
        for content in self.list_documents():
            yield content

    def list_documents(self) -> List[DocumentContent]:
        documents: List[DocumentContent] = []
        if not self.folder.exists():
            return documents

        for filepath in sorted(self.folder.rglob("*")):
            if not filepath.is_file() or filepath.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
            parser = self._parsers.get(filepath.suffix.lower())
            if not parser:
                continue

            stat = filepath.stat()
            created = datetime.fromtimestamp(stat.st_ctime)
            updated = datetime.fromtimestamp(stat.st_mtime)

            document = Document(
                id=str(uuid4()),
                source="local",
                path=str(filepath),
                title=filepath.name,
                created_at=created,
                updated_at=updated,
                tags=self.tags or None,
            )

            try:
                text = parser(filepath)
            except Exception as exc:
                # Skip files that fail to parse; ingestion service will surface errors.
                documents.append(
                    DocumentContent(document=document, text=f"[PARSING ERROR] {exc}")
                )
                continue

            documents.append(DocumentContent(document=document, text=text))

        return documents
