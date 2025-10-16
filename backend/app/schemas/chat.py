"""
Chat Pydantic schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatMessage(BaseModel):
    """Chat message schema"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None

class MessageCreate(ChatMessage):
    conversation_id: Optional[str] = None

class MessageResponse(ChatMessage):
    id: UUID
    conversation_id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatQueryRequest(BaseModel):
    """Chat query request schema"""
    query: str
    fund_id: Optional[int] = None
    conversation_id: Optional[str] = None


class SourceDocument(BaseModel):
    """Source document schema"""
    content: str
    metadata: Dict[str, Any]
    score: Optional[float] = None


class ChatQueryResponse(BaseModel):
    """Chat query response schema"""
    answer: str
    sources: List[SourceDocument] = []
    metrics: Optional[Dict[str, Any]] = None
    processing_time: Optional[float] = None


class ConversationCreate(BaseModel):
    """Conversation creation schema"""
    fund_id: Optional[int] = None


class Conversation(BaseModel):
    """Conversation schema"""
    conversation_id: UUID
    fund_id: Optional[int] = None
    messages: List[MessageResponse] = []
    created_at: datetime
    updated_at: datetime
