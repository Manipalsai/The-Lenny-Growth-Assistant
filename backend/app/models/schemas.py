from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class SourceCitation(BaseModel):
    chunk_id: str
    episode: str
    guest: str
    topic: Optional[str] = None
    passage: str
    similarity: float = Field(default=0.0, ge=0.0, le=1.0)
    source_url: Optional[str] = None

class MessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    role: str
    content: str
    sources: Optional[List[SourceCitation]] = []
    created_at: datetime

class SessionCreate(BaseModel):
    title: Optional[str] = "New Conversation"

class SessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = 0

class SessionDetailSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageSchema] = []

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=10000)
    provider_override: Optional[str] = None  # ollama | openai | anthropic
    stream: bool = True

class ArtifactCreate(BaseModel):
    session_id: str
    title: str
    type: str  # markdown | html
    content: str
    sources: Optional[List[SourceCitation]] = []

class ArtifactSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    session_id: str
    title: str
    type: str
    content: str
    version: int
    sources: Optional[List[SourceCitation]] = []
    created_at: datetime


class HealthCheckResponse(BaseModel):
    status: str
    database: Dict[str, Any]
    vector_store: Dict[str, Any]
    llm_providers: Dict[str, Any]
    version: str
