from typing import Optional
from datetime import datetime
from ..repositories.contract_repository import ContractRepository
from ..models import Contract, ContractCreate, ContractList, Statistics


class ContractService:
    """Business logic layer for contracts"""
    
    def __init__(self, repository: ContractRepository):
        self.repository = repository
    
    def get_contracts(
        self,
        page: int = 0,
        page_size: int = 100,
        category: Optional[str] = None,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ContractList:
        """Get contracts with business logic applied"""
        
        # Business rule: Limit max page size
        page_size = min(page_size, 1000)
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date must be before end_date")
        
        # Validate value range
        if min_value and max_value and min_value > max_value:
            raise ValueError("min_value must be less than max_value")
        
        skip = page * page_size
        
        contracts, total = self.repository.get_all(
            skip=skip,
            limit=page_size,
            category=category,
            min_value=min_value,
            max_value=max_value,
            start_date=start_date,
            end_date=end_date
        )
        
        return ContractList(
            contracts=[Contract.model_validate(c) for c in contracts],
            total=total,
            page=page,
            page_size=page_size,
            has_more=(skip + len(contracts)) < total
        )
    
    def get_contract(self, contract_id: int) -> Optional[Contract]:
        """Get a single contract"""
        db_contract = self.repository.get_by_id(contract_id)
        
        if not db_contract:
            return None
        
        return Contract.model_validate(db_contract)
    
    def create_contract(self, contract: ContractCreate) -> Contract:
        """Create a new contract with validation"""
        
        # Business rule: Contracts over $10M need additional validation
        if contract.contract_value > 10_000_000:
            # In real app, might trigger approval workflow
            pass
        
        # Business rule: Future contracts need special handling
        if contract.contract_date > datetime.now():
            # In real app, might set status to "pending"
            pass
        
        db_contract = self.repository.create(contract.model_dump())
        return Contract.model_validate(db_contract)
    
    def get_statistics(self) -> Statistics:
        """Get aggregated statistics"""
        stats_dict = self.repository.get_statistics()
        return Statistics(**stats_dict)
