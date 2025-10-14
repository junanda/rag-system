from .celery_app import celery_app
from app.services.document_processor import DocumentProcessor
from app.models.document import Document
import asyncio


@celery_app.task(name="task_document_process")
def task_document_process(document_id: int, file_path: str, fund_id: int):
    """Background task to process document"""
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Update status to processing
        document = db.query(Document).filter(Document.id == document_id).first()
        document.parsing_status = "processing"
        db.commit()
        
        # Process document
        processor = DocumentProcessor()
        result = asyncio.run(processor.process_document(file_path, document_id, fund_id))
        
        # Update status
        document.parsing_status = result["status"]
        if result["status"] == "failed":
            document.error_message = result.get("error")
        db.commit()
        
    except Exception as e:
        document = db.query(Document).filter(Document.id == document_id).first()
        document.parsing_status = "failed"
        document.error_message = str(e)
        db.commit()
    finally:
        db.close()