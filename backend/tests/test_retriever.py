import pytest
from app.rag.retriever import cosine_similarity, retriever
from app.database import get_db_session
from app.models.db_models import TranscriptChunkModel

def test_cosine_similarity():
    v1 = [1.0, 0.0, 0.0]
    v2 = [1.0, 0.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v2), 0.001) == 1.0

    v3 = [0.0, 1.0, 0.0]
    assert pytest.approx(cosine_similarity(v1, v3), 0.001) == 0.0

@pytest.mark.asyncio
async def test_retriever_finds_relevant_chunks():
    db = get_db_session()
    chunks, is_confident = await retriever.retrieve(db, "What is Founder Mode according to Brian Chesky?")
    assert len(chunks) > 0
    # The top result should be Brian Chesky
    assert any(c["guest"] == "Brian Chesky" for c in chunks)
    db.close()

@pytest.mark.asyncio
async def test_retriever_refuses_out_of_domain():
    db = get_db_session()
    # Completely unrelated query with very high threshold override
    chunks, is_confident = await retriever.retrieve(
        db,
        "quantum chromodynamics quark gluon plasma subatomic hadron collider",
        threshold_override=0.90
    )
    assert len(chunks) == 0 or not is_confident
    db.close()
