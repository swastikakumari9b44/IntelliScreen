"""
Tests for the token-aware chunking strategy used in ingestion.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from scripts.precompute_embeddings import chunk_page_text, _encoding, CHUNK_SIZE_TOKENS


def test_chunk_page_text_empty_returns_empty_list():
    assert chunk_page_text("") == []


def test_chunk_page_text_short_text_single_chunk():
    text = "Machine learning is a subfield of artificial intelligence."
    chunks = chunk_page_text(text)
    assert len(chunks) == 1
    assert chunks[0].strip() == text


def test_chunk_page_text_respects_max_token_size():
    # Build text long enough to require multiple chunks
    long_text = "Gradient descent is an optimization algorithm. " * 200
    chunks = chunk_page_text(long_text)
    assert len(chunks) > 1
    for chunk in chunks:
        token_count = len(_encoding.encode(chunk))
        assert token_count <= CHUNK_SIZE_TOKENS


def test_chunk_page_text_has_overlap_between_consecutive_chunks():
    long_text = "Neural networks learn representations from data. " * 200
    chunks = chunk_page_text(long_text)
    assert len(chunks) >= 2
    # Some tokens from the end of chunk[0] should reappear at the start of chunk[1]
    first_chunk_tail_tokens = set(_encoding.encode(chunks[0])[-10:])
    second_chunk_head_tokens = set(_encoding.encode(chunks[1])[:20])
    assert first_chunk_tail_tokens & second_chunk_head_tokens
