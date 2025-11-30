from pathlib import Path


def parse_text(path: Path) -> str:
    data = path.read_text(encoding="utf-8", errors="ignore")
    return data
