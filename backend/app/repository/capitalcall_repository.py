from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.transaction import CapitalCall
from app.db.session import SessionLocal

class CapitalCallRepository:
    """Repository for Capital Call operations."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def create(self, data: Dict[str, Any]) -> CapitalCall:
        """Create single capital call."""
        call = CapitalCall(**data)
        self.db.add(call)
        self.db.commit()
        self.db.refresh(call)
        return call
    
    def create_bulk(self, fund_id: int, records: List[Dict[str, Any]]) -> List[CapitalCall]:
        """Create multiple capital calls."""
        calls = []
        for record in records:
            # Parse date string to datetime
            date_str = record.get('Date')
            if isinstance(date_str, str):
                call_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                call_date = date_str
            
            call = CapitalCall(
                fund_id=fund_id,
                call_date=call_date,
                call_type=record.get('Call Number'),
                amount=record.get('Amount'),
                description=record.get('Description')
            )
            calls.append(call)
        
        self.db.add_all(calls)
        self.db.commit()
        
        for call in calls:
            self.db.refresh(call)
        
        return calls
    
    def get_by_fund(self, fund_id: int) -> List[CapitalCall]:
        """Get all capital calls for a fund."""
        return self.db.query(CapitalCall).filter(CapitalCall.fund_id == fund_id).order_by(CapitalCall.date).all()
    
    def get_by_id(self, call_id: int) -> Optional[CapitalCall]:
        """Get capital call by ID."""
        return self.db.query(CapitalCall).filter(CapitalCall.id == call_id).first()
    
    def update(self, call_id: int, data: Dict[str, Any]) -> Optional[CapitalCall]:
        """Update capital call."""
        call = self.get_by_id(call_id)
        if call:
            for key, value in data.items():
                setattr(call, key, value)
            self.db.commit()
            self.db.refresh(call)
        return call
    
    def delete(self, call_id: int) -> bool:
        """Delete capital call."""
        call = self.get_by_id(call_id)
        if call:
            self.db.delete(call)
            self.db.commit()
            return True
        return False