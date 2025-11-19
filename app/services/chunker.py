from typing import List


def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """
    Split text into overlapping chunks with simple character-based windowing.
    Ensures overlap is less than chunk size to avoid infinite loops.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    normalized = text.replace("\r\n", "\n").strip()
    if not normalized:
        return []

    chunks: List[str] = []
    start = 0
    text_length = len(normalized)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(normalized[start:end])
        if end == text_length:
            break
        start = end - overlap

    return chunks
