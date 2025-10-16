from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class MessageBase(BaseModel):
    role: str
    content: str


class MessageCreate(MessageBase):
    conversation_id: str


class MessageResponse(MessageBase):
    id: str
    conversation_id: str
    timestamp: datetime

    class Config:
        orm_mode = True


class ConversationResponse(BaseModel):
    id: str
    fund_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        orm_mode = True
