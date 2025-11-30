import re
from pathlib import Path

import markdown2


def parse_markdown(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    html = markdown2.markdown(raw)
    # Strip HTML tags to yield readable plain text for embeddings.
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()
