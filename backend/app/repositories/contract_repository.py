from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Tuple
from datetime import datetime
from ..database import Contract as DBContract, ContractCategoryEnum


class ContractRepository:
    """Data access layer for contracts"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List[DBContract], int]:
        """Get contracts with filtering and pagination"""
        query = self.db.query(DBContract)
        
        # Apply filters
        filters = []
        if category:
            filters.append(DBContract.category == category)
        if min_value:
            filters.append(DBContract.contract_value >= min_value)
        if max_value:
            filters.append(DBContract.contract_value <= max_value)
        if start_date:
            filters.append(DBContract.contract_date >= start_date)
        if end_date:
            filters.append(DBContract.contract_date <= end_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        contracts = query.offset(skip).limit(limit).all()
        
        return contracts, total
    
    def get_by_id(self, contract_id: int) -> Optional[DBContract]:
        """Get a single contract by ID"""
        return self.db.query(DBContract).filter(DBContract.id == contract_id).first()
    
    def create(self, contract_data: dict) -> DBContract:
        """Create a new contract"""
        data = dict(contract_data)
        if "category" in data and isinstance(data["category"], str):
            data["category"] = ContractCategoryEnum(data["category"])
        if "contract_date" in data and isinstance(data["contract_date"], str):
            data["contract_date"] = datetime.strptime(data["contract_date"], "%Y-%m-%d")
        contract = DBContract(**data)
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract
    
    def get_statistics(self) -> dict:
        """Get aggregated statistics"""
        stats = self.db.query(
            func.count(DBContract.id).label('count'),
            func.sum(DBContract.contract_value).label('total_value'),
            func.avg(DBContract.contract_value).label('avg_value')
        ).first()
        
        # By category
        category_stats = self.db.query(
            DBContract.category,
            func.count(DBContract.id).label('count'),
            func.sum(DBContract.contract_value).label('total_value')
        ).group_by(DBContract.category).all()
        
        return {
            'total_contracts': stats.count or 0,
            'total_value': float(stats.total_value or 0),
            'average_value': float(stats.avg_value or 0),
            'by_category': {
                str(cat.value): {
                    'count': float(count),
                    'total_value': float(total or 0)
                }
                for cat, count, total in category_stats
            }
        }
