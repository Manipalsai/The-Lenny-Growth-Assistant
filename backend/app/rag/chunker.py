import re
from typing import List, Dict, Any

class TranscriptChunker:
    """
    Intelligently breaks transcripts into semantic chunks (approx 500-800 words/tokens)
    with ~100 token overlap, preserving speaker, topic, and episode metadata.
    """

    def __init__(self, target_chunk_size: int = 600, overlap_size: int = 100):
        self.target_chunk_size = target_chunk_size
        self.overlap_size = overlap_size

    def clean_text(self, text: str) -> str:
        # Remove extra blank lines and normalize whitespace
        cleaned = re.sub(r'\r\n', '\n', text)
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        cleaned = re.sub(r'[ \t]+', ' ', cleaned)
        return cleaned.strip()

    def split_paragraphs(self, text: str) -> List[str]:
        cleaned = self.clean_text(text)
        # Split on double newlines or speaker headers like "Lenny (01:23):" or "Guest:"
        paragraphs = re.split(r'\n\n+', cleaned)
        return [p.strip() for p in paragraphs if p.strip()]

    def chunk_transcript(
        self,
        transcript_text: str,
        episode_title: str,
        guest_name: str,
        source_url: str = ""
    ) -> List[Dict[str, Any]]:
        paragraphs = self.split_paragraphs(transcript_text)
        chunks: List[Dict[str, Any]] = []

        current_words: List[str] = []
        current_topic = None

        for para in paragraphs:
            # Check for topic header or chapter title, e.g. "### Finding Product-Market Fit" or "02:15 - Growth Loops"
            header_match = re.match(r'^(?:#+\s*|\d{1,2}:\d{2}\s*[-–]\s*)(.+)$', para)
            if header_match:
                current_topic = header_match.group(1).strip()
                continue

            para_words = para.split()
            if not para_words:
                continue

            # If adding this paragraph exceeds target chunk size and we have enough words
            if len(current_words) + len(para_words) > self.target_chunk_size and len(current_words) >= 200:
                chunk_content = " ".join(current_words)
                chunk_id = f"{guest_name.lower().replace(' ', '_')}_{len(chunks) + 1}"

                chunks.append({
                    "id": chunk_id,
                    "episode": episode_title,
                    "guest": guest_name,
                    "topic": current_topic or "General Discussion",
                    "content": chunk_content,
                    "source_url": source_url
                })

                # Maintain overlap from end of current_words
                overlap_words = current_words[-self.overlap_size:] if len(current_words) > self.overlap_size else []
                current_words = overlap_words + para_words
            else:
                current_words.extend(para_words)

        if current_words:
            chunk_content = " ".join(current_words)
            chunk_id = f"{guest_name.lower().replace(' ', '_')}_{len(chunks) + 1}"
            chunks.append({
                "id": chunk_id,
                "episode": episode_title,
                "guest": guest_name,
                "topic": current_topic or "Closing Thoughts",
                "content": chunk_content,
                "source_url": source_url
            })

        return chunks

chunker = TranscriptChunker()
