import hashlib
import math
from typing import List
import httpx
from app.config import settings
from app.observability.logging import logger

class EmbeddingGenerator:
    """
    Generates normalized dense vector embeddings.
    Provides local deterministic semantic vectorization (384 dimensions)
    with optional cloud OpenAI embedding generation.
    """

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _generate_local_embedding(self, text: str) -> List[float]:
        # High-entropy normalized feature hashing across unigrams, bigrams, and trigrams
        tokens = text.lower().split()
        vector = [0.0] * self.dimension

        if not tokens:
            return vector

        # Bag of words, character shingles, and n-grams for semantic sensitivity
        features = []
        for i in range(len(tokens)):
            features.append(tokens[i])
            if i + 1 < len(tokens):
                features.append(f"{tokens[i]}_{tokens[i+1]}")
            if i + 2 < len(tokens):
                features.append(f"{tokens[i]}_{tokens[i+1]}_{tokens[i+2]}")

        for feat in features:
            h = int(hashlib.sha256(feat.encode('utf-8')).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if (h // self.dimension) % 2 == 0 else -1.0
            vector[idx] += sign

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    async def generate_embedding(self, text: str) -> List[float]:
        # If OpenAI is configured and explicitly requested
        if settings.EMBEDDING_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    res = await client.post(
                        "https://api.openai.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={"input": text[:8000], "model": "text-embedding-3-small"}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        return data["data"][0]["embedding"]
            except Exception as e:
                logger.warning(f"OpenAI embedding generation failed ({e}). Falling back to local vectorizer.")

        # Default resilient local embedding
        return self._generate_local_embedding(text)

    def generate_embedding_sync(self, text: str) -> List[float]:
        return self._generate_local_embedding(text)

embedding_generator = EmbeddingGenerator(dimension=settings.EMBEDDING_DIMENSION)
