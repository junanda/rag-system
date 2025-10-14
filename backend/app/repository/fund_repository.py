from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.fund import Fund
from app.schemas.fund import FundCreate, FundUpdate

class FundRepository:
    """Repository for Fund CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, fund_data: FundCreate) -> Fund:
        """Create new fund"""
        fund = Fund(**fund_data.model_dump())
        self.db.add(fund)
        self.db.commit()
        self.db.refresh(fund)
        return fund
    
    def get_by_id(self, fund_id: int) -> Optional[Fund]:
        """Get fund by ID"""
        return self.db.query(Fund).filter(Fund.id == fund_id).first()
    
    def get_by_name(self, name: str) -> Optional[Fund]:
        """Get fund by name"""
        return self.db.query(Fund).filter(Fund.name == name).first()
    
    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        fund_type: Optional[str] = None,
        vintage_year: Optional[int] = None
    ) -> List[Fund]:
        """Get all funds with optional filters"""
        query = self.db.query(Fund)
        
        if fund_type:
            query = query.filter(Fund.fund_type == fund_type)
        
        if vintage_year:
            query = query.filter(Fund.vintage_year == vintage_year)
        
        return query.order_by(Fund.created_at.desc()).offset(skip).limit(limit).all()
    
    def update(self, fund_id: int, fund_data: FundUpdate) -> Optional[Fund]:
        """Update fund"""
        fund = self.get_by_id(fund_id)
        if not fund:
            return None
        
        update_data = fund_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(fund, key, value)
        
        fund.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(fund)
        return fund
    
    def delete(self, fund_id: int) -> bool:
        """Delete fund"""
        fund = self.get_by_id(fund_id)
        if not fund:
            return False
        
        self.db.delete(fund)
        self.db.commit()
        return True
    
    def get_with_documents(self, fund_id: int) -> Optional[Fund]:
        """Get fund with all documents"""
        return self.db.query(Fund).filter(Fund.id == fund_id).first()
    
    def count(self) -> int:
        """Count total funds"""
        return self.db.query(Fund).count()
    
    def search(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Fund]:
        """Search funds by name or GP name"""
        search_pattern = f"%{search_term}%"
        return self.db.query(Fund).filter(
            (Fund.name.ilike(search_pattern)) | 
            (Fund.gp_name.ilike(search_pattern))
        ).offset(skip).limit(limit).all()