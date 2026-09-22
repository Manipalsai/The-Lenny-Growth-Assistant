from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import ArtifactModel, SessionModel
from app.models.schemas import ArtifactSchema, ArtifactCreate
from app.security.artifact_security import artifact_security

router = APIRouter(prefix="/api/artifacts", tags=["Artifacts"])

@router.get("/{artifact_id}", response_model=ArtifactSchema)
def get_artifact(artifact_id: str, db: Session = Depends(get_db)):
    artifact = db.query(ArtifactModel).filter(ArtifactModel.id == artifact_id).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact

@router.get("/session/{session_id}", response_model=List[ArtifactSchema])
def list_session_artifacts(session_id: str, db: Session = Depends(get_db)):
    artifacts = db.query(ArtifactModel).filter(ArtifactModel.session_id == session_id).order_by(ArtifactModel.created_at.desc()).all()
    return artifacts

@router.post("", response_model=ArtifactSchema)
def create_artifact(payload: ArtifactCreate, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == payload.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    content = payload.content
    if payload.type == "html":
        content, _ = artifact_security.sanitize_html(content)

    new_artifact = ArtifactModel(
        session_id=payload.session_id,
        title=payload.title,
        type=payload.type,
        content=content,
        sources=[s.dict() for s in payload.sources] if payload.sources else []
    )
    db.add(new_artifact)
    db.commit()
    db.refresh(new_artifact)
    return new_artifact
