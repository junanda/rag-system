from sqlalchemy.orm import Session
from app.models.conversation import Conversation, Message
from app.schemas.chat import ConversationCreate, MessageCreate
from datetime import datetime
from app.db.session import SessionLocal
import uuid

class ConversationRepository:

    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()

    def create_conversation(self, data: ConversationCreate):
        new_conv = Conversation(fund_id=data.fund_id)
        self.db.add(new_conv)
        self.db.commit()
        self.db.refresh(new_conv)
        return new_conv

    def get_conversation(self, conversation_id):
        return self.db.query(Conversation).filter(Conversation.id == uuid.UUID(conversation_id)).first()
    
    def get_conversation_history(self, conversation_id):
        return self.db.query(Message).filter(Message.conversation_id == uuid.UUID(conversation_id)).all()

    def get_all_conversations(self):
        return self.db.query(Conversation).all()

    def add_message(self, conversation_id, message: MessageCreate):
        new_msg = Message(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            timestamp=datetime.utcnow(),
        )
        self.db.add(new_msg)
        self.db.commit()
        self.db.refresh(new_msg)
        self.update_timestamp(conversation_id)
        return new_msg

    def update_timestamp(self, conversation_id):
        conv = self.db.query(Conversation).filter(Conversation.id == uuid.UUID(conversation_id)).first()
        if conv:
            conv.updated_at = datetime.utcnow()
            self.db.commit()
        return conv

    def delete_conversation(self, conversation_id):
        conv = self.db.query(Conversation).filter(Conversation.id == uuid.UUID(conversation_id)).first()
        if conv:
            self.db.delete(conv)
            self.db.commit()
        return True
