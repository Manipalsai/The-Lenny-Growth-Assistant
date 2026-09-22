import pytest
from app.rag.chunker import chunker

def test_clean_text():
    raw = "Hello   world!\r\n\r\n\r\nThis is   a test."
    cleaned = chunker.clean_text(raw)
    assert "\r" not in cleaned
    assert "   " not in cleaned

def test_chunking_preserves_metadata():
    text = """
Lenny (01:00): Welcome Brian Chesky to the show.

Brian Chesky (01:10): Being in the details is what founder mode is all about. You cannot delegate the soul of your company.
"""
    chunks = chunker.chunk_transcript(
        transcript_text=text,
        episode_title="Founder Mode",
        guest_name="Brian Chesky",
        source_url="https://example.com"
    )
    assert len(chunks) >= 1
    chunk = chunks[0]
    assert chunk["guest"] == "Brian Chesky"
    assert chunk["episode"] == "Founder Mode"
    assert "Founder mode" in chunk["content"] or "founder mode" in chunk["content"]
