import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.observability.logging import logger
from app.models.db_models import Base

# Engine initialization with fallback capability
engine = None
SessionLocal = None
is_sqlite_fallback = False

def init_db():
    global engine, SessionLocal, is_sqlite_fallback
    db_url = settings.DATABASE_URL

    try:
        # Attempt PostgreSQL connection
        test_engine = create_engine(db_url, pool_pre_ping=True, connect_args={"connect_timeout": 3})
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            # Attempt to create vector extension if pgvector is available
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            except Exception as ext_err:
                logger.warning(f"Could not initialize pgvector extension: {ext_err}")
        engine = test_engine
        logger.info("Successfully connected to primary PostgreSQL database.")
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK:
            logger.warning(f"PostgreSQL connection failed ({e}). Falling back to local SQLite database: {settings.SQLITE_DB_PATH}")
            sqlite_url = f"sqlite:///{settings.SQLITE_DB_PATH}"
            engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
            is_sqlite_fallback = True
        else:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise e

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

def get_db_session() -> Session:
    if SessionLocal is None:
        init_db()
    return SessionLocal()

def get_db():
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()

