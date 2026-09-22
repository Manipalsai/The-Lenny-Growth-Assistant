from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import SessionModel, MessageModel, ArtifactModel
from app.models.schemas import SessionSchema, SessionCreate, SessionDetailSchema

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])

@router.post("", response_model=SessionSchema)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    new_session = SessionModel(title=payload.title or "New Conversation")
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("", response_model=List[SessionSchema])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    result = []
    for s in sessions:
        msg_count = db.query(MessageModel).filter(MessageModel.session_id == s.id).count()
        result.append(SessionSchema(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=msg_count
        ))
    return result

@router.get("/{session_id}", response_model=SessionDetailSchema)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(session)
    db.commit()
    return {"status": "success", "deleted_id": session_id}
