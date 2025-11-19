import pytest

from app.services.chunker import chunk_text


def test_chunk_text_basic_overlap():
    text = "abcdefghijklmnopqrstuvwxyz"
    chunks = chunk_text(text, chunk_size=10, overlap=2)
    assert chunks[0] == "abcdefghij"
    # second chunk starts 2 chars before the prior ended
    assert chunks[1].startswith("ij")
    # ensure final chunk covers end
    assert chunks[-1].endswith("z")
    assert len(chunks) == 3


def test_chunk_text_empty():
    assert chunk_text("", chunk_size=5, overlap=1) == []


def test_chunk_text_invalid_params():
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=0, overlap=1)
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=5, overlap=5)
