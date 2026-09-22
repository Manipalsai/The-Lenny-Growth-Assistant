import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.config import settings
from app.models.db_models import TranscriptChunkModel
from app.rag.embeddings import embedding_generator
from app.observability.logging import logger

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)

class RAGRetriever:
    """
    Handles dense vector retrieval, similarity filtering,
    source diversity balancing, and grounding confidence assessment.
    """

    @property
    def threshold(self) -> float:
        return settings.SIMILARITY_THRESHOLD

    @property
    def top_k(self) -> int:
        return settings.TOP_K_CHUNKS

    async def retrieve(
        self,
        db: Session,
        query: str,
        threshold_override: float = None,
        top_k_override: int = None
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Returns (ranked_chunks, is_confident)
        """
        threshold = threshold_override if threshold_override is not None else self.threshold
        top_k = top_k_override if top_k_override is not None else self.top_k

        query_embedding = await embedding_generator.generate_embedding(query)
        all_chunks = db.query(TranscriptChunkModel).all()

        if not all_chunks:
            logger.warning("No transcript chunks found in database.")
            return [], False

        scored_chunks: List[Tuple[float, TranscriptChunkModel]] = []
        for chunk in all_chunks:
            emb = chunk.embedding
            if isinstance(emb, list):
                score = cosine_similarity(query_embedding, emb)
                if score >= threshold:
                    scored_chunks.append((score, chunk))

        # Sort descending by similarity score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        # Apply source diversity: allow max 2 chunks per guest in the top results
        selected_chunks: List[Dict[str, Any]] = []
        guest_count: Dict[str, int] = {}

        for score, chunk in scored_chunks:
            guest = chunk.guest
            if guest_count.get(guest, 0) >= 2 and len(selected_chunks) < top_k:
                continue

            guest_count[guest] = guest_count.get(guest, 0) + 1
            selected_chunks.append({
                "chunk_id": chunk.id,
                "episode": chunk.episode,
                "guest": chunk.guest,
                "topic": chunk.topic or "Key Insight",
                "passage": chunk.content,
                "similarity": round(score, 3),
                "source_url": chunk.source_url or ""
            })

            if len(selected_chunks) >= top_k:
                break

        is_confident = len(selected_chunks) > 0 and selected_chunks[0]["similarity"] >= threshold
        logger.info(f"Retrieved {len(selected_chunks)} chunks for query '{query[:50]}...' (Confidence: {is_confident})")
        return selected_chunks, is_confident

retriever = RAGRetriever()
