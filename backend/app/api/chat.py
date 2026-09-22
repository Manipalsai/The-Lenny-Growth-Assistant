import json
import time
import uuid
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import SessionModel, MessageModel, ArtifactModel
from app.models.schemas import ChatRequest
from app.rag.retriever import retriever
from app.rag.citation import citation_manager
from app.skills.router import router as intent_router
from app.skills.grounded_qa import grounded_qa
from app.skills.ship30_writer import ship30_writer
from app.skills.artifact_generator import artifact_generator
from app.security.artifact_security import artifact_security
from app.providers.factory import provider_factory
from app.config import settings
from app.observability.logging import logger

router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("")
async def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    # 1. Validate or initialize session
    session = None
    if payload.session_id:
        session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()

    if not session:
        # Create session with title derived from first prompt
        title = payload.message[:40] + ("..." if len(payload.message) > 40 else "")
        session = SessionModel(id=payload.session_id or str(uuid.uuid4()), title=title)
        db.add(session)
        db.commit()
        db.refresh(session)

    # 2. Persist User Message
    user_msg = MessageModel(
        session_id=session.id,
        role="user",
        content=payload.message
    )
    db.add(user_msg)
    db.commit()

    # 3. Retrieve conversation history for context
    history_records = db.query(MessageModel).filter(
        MessageModel.session_id == session.id
    ).order_by(MessageModel.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in history_records[:-1]]

    # 4. Stream Generator
    async def sse_event_stream() -> AsyncGenerator[str, None]:
        start_time = time.time()
        yield f"event: status\ndata: {json.dumps({'status': 'searching', 'message': 'Searching Lenny podcast transcripts...'})}\n\n"

        # RAG Retrieval
        retrieved_chunks, is_confident = await retriever.retrieve(db, payload.message)

        yield f"event: status\ndata: {json.dumps({'status': 'retrieved', 'chunk_count': len(retrieved_chunks), 'confident': is_confident})}\n\n"

        # Check for out-of-domain / insufficient evidence
        if not retrieved_chunks:
            refusal_text = (
                "Based on the available Lenny's Podcast transcript archive, there is insufficient evidence "
                "to answer this question. The current knowledge base covers product management, growth loops, "
                "metrics, hiring, pricing, and company building from Lenny's interviews. "
                "Please try asking a question related to these topics or specific podcast guests."
            )
            yield f"event: text\ndata: {json.dumps({'delta': refusal_text})}\n\n"

            # Save assistant response
            asst_msg = MessageModel(
                session_id=session.id,
                role="assistant",
                content=refusal_text,
                sources=[]
            )
            db.add(asst_msg)
            db.commit()

            yield f"event: done\ndata: {json.dumps({'session_id': session.id, 'sources': []})}\n\n"
            return

        # Determine Skill & Intent
        intent = intent_router.classify_intent(payload.message)
        logger.info(f"Classified intent: {intent} for query: {payload.message[:50]}")

        if intent == "ship30_essay":
            prompt_messages = ship30_writer.build_prompt(payload.message, retrieved_chunks)
        elif intent in ["html_artifact", "markdown_artifact"]:
            art_type = "html" if intent == "html_artifact" else "markdown"
            prompt_messages = artifact_generator.build_prompt(payload.message, art_type, retrieved_chunks)
        else:
            prompt_messages = grounded_qa.build_prompt(payload.message, retrieved_chunks, history)

        # Select Provider with Fallback
        provider = provider_factory.get_provider(payload.provider_override)
        active_provider_name = provider.name
        yield f"event: provider\ndata: {json.dumps({'provider': active_provider_name})}\n\n"

        full_response = ""
        try:
            async for token in provider.stream(prompt_messages):
                full_response += token
                yield f"event: text\ndata: {json.dumps({'delta': token})}\n\n"
        except Exception as e:
            logger.warning(f"Primary provider {active_provider_name} failed: {e}")
            if settings.ENABLE_FALLBACK and active_provider_name != "openai" and settings.OPENAI_API_KEY:
                fallback_provider = provider_factory.get_fallback_provider()
                logger.info(f"Falling back to {fallback_provider.name} provider.")
                yield f"event: provider\ndata: {json.dumps({'provider': fallback_provider.name, 'fallback': True})}\n\n"
                try:
                    async for token in fallback_provider.stream(prompt_messages):
                        full_response += token
                        yield f"event: text\ndata: {json.dumps({'delta': token})}\n\n"
                except Exception as fb_err:
                    err_msg = f"\n\n[System Notice: Provider error ({e}), and fallback error ({fb_err}).]"
                    yield f"event: text\ndata: {json.dumps({'delta': err_msg})}\n\n"
                    full_response += err_msg
            else:
                err_msg = f"\n\n[Notice: LLM provider '{active_provider_name}' error: {str(e)}. If running locally, please ensure Ollama is running or configure OPENAI_API_KEY in .env.]"
                yield f"event: text\ndata: {json.dumps({'delta': err_msg})}\n\n"
                full_response += err_msg

        # Validate Citations
        cited_sources = citation_manager.validate_citations(full_response, retrieved_chunks)

        # Handle Artifact Creation if intent was artifact or essay
        artifact_id = None
        if intent in ["html_artifact", "markdown_artifact", "ship30_essay"]:
            default_type = "html" if intent == "html_artifact" else "markdown"
            title, extracted_type, clean_content = artifact_generator.extract_artifact(full_response, default_type)
            if extracted_type == "html":
                clean_content, _ = artifact_security.sanitize_html(clean_content)

            new_artifact = ArtifactModel(
                session_id=session.id,
                title=title,
                type=extracted_type,
                content=clean_content,
                sources=cited_sources
            )
            db.add(new_artifact)
            db.commit()
            db.refresh(new_artifact)
            artifact_id = new_artifact.id

            yield f"event: artifact\ndata: {json.dumps({'id': new_artifact.id, 'title': title, 'type': extracted_type, 'content': clean_content})}\n\n"

        # Persist assistant message in DB
        asst_msg = MessageModel(
            session_id=session.id,
            role="assistant",
            content=full_response,
            sources=cited_sources
        )
        db.add(asst_msg)
        db.commit()

        latency_ms = round((time.time() - start_time) * 1000, 2)
        yield f"event: done\ndata: {json.dumps({'session_id': session.id, 'sources': cited_sources, 'artifact_id': artifact_id, 'latency_ms': latency_ms})}\n\n"

    return StreamingResponse(sse_event_stream(), media_type="text/event-stream")
