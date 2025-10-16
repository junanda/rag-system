# app/services/conversation_service.py
from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import Depends

from app.db.session import get_db
from app.repository.conversation_repository import ConversationRepository
from app.models.conversation import Conversation, Message
from app.schemas.chat import ConversationCreate, MessageCreate

def get_conversation_repo(db: Session = Depends(get_db)) -> ConversationRepository:
    return ConversationRepository(db)

# Dependency factory
def get_conversation_service(
    conv_repo: ConversationRepository = Depends(get_conversation_repo)
):
    return ConversationService(conv_repo)


class ConversationService:
    """Business logic layer for managing conversations and messages"""

    def __init__(self,conv_repo: ConversationRepository):
        self.conv_repo = conv_repo

    # Create new conversation
    async def create_conversation(self, fund_id: str) -> Conversation:
        conversation = self.conv_repo.create_conversation(
            data=ConversationCreate(
                fund_id=fund_id
            )
        )
        return conversation

    # Get existing conversation
    async def get_conversation(self, conversation_id: str) -> Conversation:
        conversation = self.conv_repo.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        conversation.messages = self.conv_repo.get_conversation_history(conversation_id)
        return conversation

    # Add a message to conversation
    async def add_message(self, conversation_id: str, role: str, content: str) -> Message:
        if not conversation_id:
            raise HTTPException(status_code=400, detail="conversation_id is required to add a message")
        message = self.conv_repo.add_message(
            conversation_id,
            MessageCreate(
                role=role,
                content=content,
                timestamp=datetime.utcnow()
            )
        )
        return message

    # Get all messages for a conversation
    async def get_conversation_history(self, conversation_id: str) -> List[Message]:
        message = self.conv_repo.get_conversation_history(conversation_id)
        return message

    # Delete a conversation (optional)
    async def delete_conversation(self, conversation_id: str) -> None:
        success = self.conv_repo.delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="Conversation not found")
