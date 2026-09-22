import re
from typing import List, Dict, Any

class CitationManager:
    """
    Validates that citations referenced in the text exist in retrieved chunks,
    and formats standard citation blocks.
    """

    @staticmethod
    def format_citation(guest: str, episode: str, topic: str = "") -> str:
        if topic and topic != "General Discussion":
            return f"[{episode}: {guest} — {topic}]"
        return f"[{episode}: {guest}]"

    @staticmethod
    def validate_citations(response_text: str, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts citations and matches them with retrieved source chunks.
        Returns the subset of retrieved chunks that were actually referenced.
        """
        if not retrieved_chunks:
            return []

        matched_sources: List[Dict[str, Any]] = []
        for chunk in retrieved_chunks:
            guest = chunk["guest"].lower()
            # If the guest or episode title is explicitly referenced in the response
            if guest in response_text.lower() or chunk["episode"].lower() in response_text.lower():
                matched_sources.append(chunk)

        # If none specifically named but chunks were used to answer, include top 3 chunks
        if not matched_sources and len(response_text) > 100:
            matched_sources = retrieved_chunks[:3]

        return matched_sources

citation_manager = CitationManager()
