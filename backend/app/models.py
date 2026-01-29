from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from enum import Enum


class ContractCategory(str, Enum):
    GOODS = "goods"
    SERVICES = "services"
    WORKS = "works"


class ContractBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    contract_value: float = Field(..., gt=0, description="Contract value in USD")
    contract_date: datetime
    category: ContractCategory
    description: Optional[str] = None


class ContractCreate(ContractBase):
    pass


class Contract(ContractBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ContractList(BaseModel):
    contracts: list[Contract]
    total: int
    page: int
    page_size: int
    has_more: bool


class Statistics(BaseModel):
    total_contracts: int
    total_value: float
    average_value: float
    by_category: dict[str, dict[str, float]]
