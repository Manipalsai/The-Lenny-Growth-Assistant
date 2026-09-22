from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.observability.logging import logger
from app.api import health, sessions, chat, artifacts

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing Lenny Growth Assistant backend...")
    init_db()
    logger.info("Backend initialization complete.")
    yield
    logger.info("Shutting down Lenny Growth Assistant backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI Knowledge & Growth Assistant over Lenny's Podcast Transcripts",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health.router)
app.include_router(sessions.router)
app.include_router(chat.router)
app.include_router(artifacts.router)

@app.get("/")
def root():
    return {
        "message": "Welcome to The Lenny Growth Assistant API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
