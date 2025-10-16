"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime
from app.db.session import get_db
from app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ConversationCreate,
    Conversation,
    MessageResponse,
)
from app.services.query_engine import QueryEngine, get_query_engine_service
from app.services.conversation import get_conversation_service, ConversationService
from app.utils.helpers import is_error_response

router = APIRouter()

# In-memory conversation storage (replace with Redis/DB in production)
conversations: Dict[str, Dict[str, Any]] = {}

@router.post("/query", response_model=ChatQueryResponse)
async def process_chat_query(
    request: ChatQueryRequest,
    conversation_service: ConversationService = Depends(get_conversation_service),
    query_engine_service: QueryEngine = Depends(get_query_engine_service)
):
    """Process a chat query using RAG"""
    
    # Get conversation history if conversation_id provided
    conversation_history = []
    if request.conversation_id:
        conversation = await conversation_service.get_conversation(request.conversation_id)
        if conversation:
            conversation_history = conversation.messages

    await conversation_service.add_message(
            conversation_id=request.conversation_id,
            role="user",
            content=request.query
        )
    
    # Process query
    response = await query_engine_service.process_query(
        query=request.query,
        fund_id=request.fund_id,
        conversation_history=conversation_history
    )
    
    await conversation_service.add_message(
        conversation_id=request.conversation_id,
        role="assistant",
        content=response["answer"] if response["answer"] and not is_error_response(response["answer"]) else ""
    )
    
    return ChatQueryResponse(**response)


@router.post("/conversations", response_model=Conversation)
async def create_conversation(request: 
    ConversationCreate,
    conversation_service: ConversationService = Depends(get_conversation_service)
    ):
    """Create a new conversation"""
    # conversation_id = str(uuid.uuid4())
    fund_id = request.fund_id or 1
    conversation = await conversation_service.create_conversation(
        fund_id=fund_id
    )
    
    return Conversation(
        conversation_id=str(conversation.id),
        fund_id=request.fund_id,
        messages=[],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str, conversation_service: ConversationService = Depends(get_conversation_service)):
    """Get conversation history"""
    conversation = await conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return Conversation(
        conversation_id=conversation_id,
        fund_id=conversation.fund_id,
        messages=[MessageResponse.model_validate(msg, from_attributes=True) for msg in conversation.messages],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str, conversation_service: ConversationService = Depends(get_conversation_service)):
    """Delete a conversation"""
    conversation = await conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    await conversation_service.delete_conversation(conversation_id)
    
    return {"message": "Conversation deleted successfully"}
