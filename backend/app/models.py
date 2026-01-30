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
    source: Optional[str] = None
    external_id: Optional[str] = None
    country: Optional[str] = None


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


class ScraperSource(BaseModel):
    """Configuration for a scraper source"""
    name: str
    method: str  # "api", "ai", "browser"
    priority: int
    url: str
    enabled: bool = True


class ContractPreview(BaseModel):
    """Preview of a contract found during scraping"""
    company_name: str
    contract_value: float
    contract_date: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    external_id: Optional[str] = None
    country: Optional[str] = None
    is_duplicate: bool = False
    duplicate_reason: Optional[str] = None


class ScraperResult(BaseModel):
    """Result from a scraping operation"""
    source: str
    contracts_found: int
    contracts_saved: int
    duplicates_skipped: int
    errors: list[str] = []
    duration_seconds: float
    contract_previews: list[ContractPreview] = []


class ScraperStatus(BaseModel):
    """Overall scraping job status"""
    status: str  # "idle", "running", "completed", "failed"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_sources: int
    completed_sources: int
    results: list[ScraperResult] = []
