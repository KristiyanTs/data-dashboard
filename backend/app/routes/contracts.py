from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from ..database import get_db
from ..models import Contract, ContractCreate, ContractList, Statistics
from ..repositories.contract_repository import ContractRepository
from ..services.contract_service import ContractService

router = APIRouter(prefix="/contracts", tags=["contracts"])


def get_contract_service(db: Session = Depends(get_db)) -> ContractService:
    """Dependency injection for ContractService"""
    repository = ContractRepository(db)
    return ContractService(repository)


@router.get("", response_model=ContractList)
async def get_contracts(
    page: int = Query(0, ge=0),
    page_size: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    min_value: Optional[float] = Query(None, ge=0),
    max_value: Optional[float] = Query(None, ge=0),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    service: ContractService = Depends(get_contract_service)
):
    """
    Get contracts with filtering and pagination.
    
    - **page**: Page number (0-indexed)
    - **page_size**: Number of items per page (max 1000)
    - **category**: Filter by category (goods, services, works)
    - **min_value**: Minimum contract value
    - **max_value**: Maximum contract value
    - **start_date**: Filter contracts from this date
    - **end_date**: Filter contracts until this date
    """
    try:
        return service.get_contracts(
            page=page,
            page_size=page_size,
            category=category,
            min_value=min_value,
            max_value=max_value,
            start_date=start_date,
            end_date=end_date
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics", response_model=Statistics)
async def get_statistics(
    service: ContractService = Depends(get_contract_service)
):
    """Get aggregated contract statistics"""
    return service.get_statistics()


@router.get("/{contract_id}", response_model=Contract)
async def get_contract(
    contract_id: int,
    service: ContractService = Depends(get_contract_service)
):
    """Get a specific contract by ID"""
    contract = service.get_contract(contract_id)
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    return contract


@router.post("", response_model=Contract, status_code=201)
async def create_contract(
    contract: ContractCreate,
    service: ContractService = Depends(get_contract_service)
):
    """Create a new contract"""
    return service.create_contract(contract)
