from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable, List

from app.models.document import DocumentContent


class DocumentSource(ABC):
    @abstractmethod
    def load(self) -> Iterable[DocumentContent]:
        ...

    @abstractmethod
    def list_documents(self) -> List[DocumentContent]:
        ...
