from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.transaction import Distribution
from app.db.session import SessionLocal

class DistributionRepository:
    """Repository for Distribution operations."""
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def create(self, data: Dict[str, Any]) -> Distribution:
        """Create single distribution."""
        dist = Distribution(**data)
        self.db.add(dist)
        self.db.commit()
        self.db.refresh(dist)
        return dist
    
    def create_bulk(self, fund_id: int, records: List[Dict[str, Any]]) -> List[Distribution]:
        """Create multiple distributions."""
        distributions = []
        for record in records:
            # Parse date
            date_str = record.get('Date')
            if isinstance(date_str, str):
                distribution_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            else:
                distribution_date = date_str
            
            # Parse recallable
            recallable_str = record.get('Recallable', 'No')
            is_recallable = recallable_str.lower() in ['yes', 'true', '1']
            
            dist = Distribution(
                fund_id=fund_id,
                distribution_date=distribution_date,
                distribution_type=record.get('Type'),
                amount=record.get('Amount'),
                is_recallable=is_recallable,
                description=record.get('Description')
            )
            distributions.append(dist)
        
        self.db.add_all(distributions)
        self.db.commit()
        
        for dist in distributions:
            self.db.refresh(dist)
        
        return distributions
    
    def get_by_fund(self, fund_id: int) -> List[Distribution]:
        """Get all distributions for a fund."""
        return self.db.query(Distribution).filter(Distribution.fund_id == fund_id).order_by(Distribution.date).all()
    
    def get_by_id(self, dist_id: int) -> Optional[Distribution]:
        """Get distribution by ID."""
        return self.db.query(Distribution).filter(Distribution.id == dist_id).first()
    
    def update(self, dist_id: int, data: Dict[str, Any]) -> Optional[Distribution]:
        """Update distribution."""
        dist = self.get_by_id(dist_id)
        if dist:
            for key, value in data.items():
                setattr(dist, key, value)
            self.db.commit()
            self.db.refresh(dist)
        return dist
    
    def delete(self, dist_id: int) -> bool:
        """Delete distribution."""
        dist = self.get_by_id(dist_id)
        if dist:
            self.db.delete(dist)
            self.db.commit()
            return True
        return False