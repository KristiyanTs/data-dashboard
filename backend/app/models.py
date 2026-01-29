from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, Any
from enum import Enum


class ContractCategory(str, Enum):
    GOODS = "goods"
    SERVICES = "services"
    WORKS = "works"


class ContractBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    contract_value: float = Field(..., gt=0, description="Contract value in USD")
    contract_date: datetime

    @field_validator("contract_date", mode="before")
    @classmethod
    def parse_contract_date(cls, v: Any) -> Any:
        """Accept date-only string (YYYY-MM-DD) and coerce to datetime at midnight."""
        if isinstance(v, str) and len(v) == 10 and v.count("-") == 2:
            return datetime.strptime(v, "%Y-%m-%d")
        return v
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
