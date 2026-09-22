from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, is_sqlite_fallback
from app.models.db_models import TranscriptChunkModel
from app.providers.factory import provider_factory
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
async def check_health(db: Session = Depends(get_db)):
    # 1. Database Health
    db_status = "healthy"
    db_type = "sqlite" if is_sqlite_fallback else "postgresql"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # 2. Vector Store Health
    chunk_count = 0
    vector_status = "healthy"
    try:
        chunk_count = db.query(TranscriptChunkModel).count()
        if chunk_count == 0:
            vector_status = "empty (run ingest.py to load transcripts)"
    except Exception as e:
        vector_status = f"unhealthy: {str(e)}"

    # 3. LLM Providers Health
    ollama_provider = provider_factory.get_provider("ollama")
    ollama_health = await ollama_provider.health_check()

    cloud_provider = provider_factory.get_fallback_provider()
    cloud_health = await cloud_provider.health_check()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": {
            "status": db_status,
            "type": db_type,
            "sqlite_fallback": is_sqlite_fallback
        },
        "vector_store": {
            "status": vector_status,
            "total_chunks": chunk_count,
            "embedding_dimension": settings.EMBEDDING_DIMENSION
        },
        "llm_providers": {
            "active_provider": settings.LLM_PROVIDER,
            "fallback_enabled": settings.ENABLE_FALLBACK,
            "ollama": ollama_health,
            "cloud": cloud_health
        },
        "version": settings.VERSION
    }
