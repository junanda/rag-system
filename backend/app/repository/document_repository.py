from datetime import datetime
from typing import List, Optional
from app.db.session import SessionLocal
from sqlalchemy.orm import Session
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentUpdate

class DocumentRepository:
    """Repository for Document CRUD operations"""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def create(self, doc_data: DocumentCreate) -> Document:
        """Create new document"""
        document = Document(**doc_data.model_dump())
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def get_by_id(self, doc_id: int) -> Optional[Document]:
        """Get document by ID"""
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def get_by_fund(
        self, 
        fund_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Document]:
        """Get all documents for a fund"""
        return self.db.query(Document)\
            .filter(Document.fund_id == fund_id)\
            .order_by(Document.upload_date.desc())\
            .offset(skip).limit(limit).all()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        parsing_status: Optional[str] = None
    ) -> List[Document]:
        """Get all documents with optional status filter"""
        query = self.db.query(Document)
        
        if parsing_status:
            query = query.filter(Document.parsing_status == parsing_status)
        
        return query.order_by(Document.upload_date.desc()).offset(skip).limit(limit).all()
    
    def update(self, doc_id: int, doc_data: DocumentUpdate) -> Optional[Document]:
        """Update document"""
        document = self.get_by_id(doc_id)
        if not document:
            return None
        
        update_data = doc_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(document, key, value)
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def update_status(
        self, 
        doc_id: int, 
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[Document]:
        """Update document parsing status"""
        document = self.get_by_id(doc_id)
        if not document:
            return None
        
        document.parsing_status = status
        if error_message:
            document.error_message = error_message
        
        document.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(document)
        return document
    
    def delete(self, doc_id: int) -> bool:
        """Delete document"""
        document = self.get_by_id(doc_id)
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        return True
    
    def get_with_fund(self, doc_id: int) -> Optional[Document]:
        """Get document with fund information"""
        return self.db.query(Document).filter(Document.id == doc_id).first()
    
    def count_by_fund(self, fund_id: int) -> int:
        """Count documents for a fund"""
        return self.db.query(Document).filter(Document.fund_id == fund_id).count()
    
    def count_by_status(self, status: str) -> int:
        """Count documents by status"""
        return self.db.query(Document).filter(Document.parsing_status == status).count()
    
    def get_pending_documents(self, limit: int = 10) -> List[Document]:
        """Get pending documents for processing"""
        return self.db.query(Document)\
            .filter(Document.parsing_status == "pending")\
            .order_by(Document.upload_date.asc())\
            .limit(limit).all()
    
    def get_failed_documents(self, skip: int = 0, limit: int = 100) -> List[Document]:
        """Get failed documents"""
        return self.db.query(Document)\
            .filter(Document.parsing_status == "failed")\
            .order_by(Document.upload_date.desc())\
            .offset(skip).limit(limit).all()