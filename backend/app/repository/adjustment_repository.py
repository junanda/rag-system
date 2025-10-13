from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.transaction import Adjustment
from app.db.session import SessionLocal

class AdjustmentRepository:
    """Repository for Adjustment operations."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def create(self, data: Dict[str, Any]) -> Adjustment:
        """Create single adjustment."""
        adj = Adjustment(**data)
        self.db.add(adj)
        self.db.commit()
        self.db.refresh(adj)
        return adj
    
    def create_bulk(self, fund_id: int, records: List[Dict[str, Any]]) -> List[Adjustment]:
        """Create multiple adjustments."""
        adjustments = []
        for record in records:
            # Parse date
            date_str = record.get('Date')
            if isinstance(date_str, str):
                adjustment_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                adjustment_date = date_str
            
            adj = Adjustment(
                fund_id=fund_id,
                adjustment_date=adjustment_date,
                adjustment_type=record.get('Type'),
                amount=record.get('Amount'),
                description=record.get('Description')
            )
            adjustments.append(adj)
        
        self.db.add_all(adjustments)
        self.db.commit()
        
        for adj in adjustments:
            self.db.refresh(adj)
        
        return adjustments
    
    def get_by_fund(self, fund_id: int) -> List[Adjustment]:
        """Get all adjustments for a fund."""
        return self.db.query(Adjustment).filter(Adjustment.fund_id == fund_id).order_by(Adjustment.date).all()
    
    def get_by_id(self, adj_id: int) -> Optional[Adjustment]:
        """Get adjustment by ID."""
        return self.db.query(Adjustment).filter(Adjustment.id == adj_id).first()
    
    def update(self, adj_id: int, data: Dict[str, Any]) -> Optional[Adjustment]:
        """Update adjustment."""
        adj = self.get_by_id(adj_id)
        if adj:
            for key, value in data.items():
                setattr(adj, key, value)
            self.db.commit()
            self.db.refresh(adj)
        return adj
    
    def delete(self, adj_id: int) -> bool:
        """Delete adjustment."""
        adj = self.get_by_id(adj_id)
        if adj:
            self.db.delete(adj)
            self.db.commit()
            return True
        return False