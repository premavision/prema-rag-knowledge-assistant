from pathlib import Path

from pypdf import PdfReader


def parse_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            # Skip pages that fail to extract cleanly.
            continue
    return "\n".join(texts).strip()
